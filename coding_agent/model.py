"""One observable JSON/multimodal client with a single bounded retry policy."""

import time
from uuid import uuid4

import httpx
from openai import (
    OpenAI,
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
    RateLimitError,
)

from coding_agent.protocol import BudgetExhausted, parse_action


class Model:
    def __init__(self, config, trace):
        self.config, self.trace = config, trace
        self.active_call = None

        def http_response(response):
            trace.emit(
                "http.response",
                call_id=self.active_call,
                status_code=response.status_code,
                request_id=response.headers.get("x-request-id"),
            )

        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            max_retries=0,
            http_client=httpx.Client(event_hooks={"response": [http_response]}),
        )

    def generate(self, messages, remaining):
        config, trace = self.config, self.trace
        if remaining < 1 or trace.tokens + config.output_tokens > config.max_tokens:
            raise BudgetExhausted("No remaining model allowance")
        for attempt in range(config.transport_retries + 1):
            call_id = uuid4().hex
            self.active_call = call_id
            arguments = {
                "model": config.model,
                "messages": messages,
                "response_format": {"type": "json_object"},
                "max_completion_tokens": config.output_tokens,
                "extra_body": {"thinking": {"type": "disabled"}},
            }
            trace.emit(
                "model.request",
                call_id=call_id,
                attempt=attempt,
                artifact=trace.artifact("request", arguments),
            )
            started = time.monotonic()
            try:
                response = self.client.with_options(
                    timeout=min(180, remaining)
                ).chat.completions.create(**arguments)
            except (
                APIConnectionError,
                APITimeoutError,
                InternalServerError,
                RateLimitError,
            ) as error:
                trace.evidence_complete = False
                trace.emit(
                    "model.error",
                    call_id=call_id,
                    error_type=type(error).__name__,
                    seconds=time.monotonic() - started,
                )
                remaining -= time.monotonic() - started
                if attempt == config.transport_retries or remaining < 3:
                    raise RuntimeError(
                        "TRANSPORT_FAILED: " + type(error).__name__
                    ) from error
                time.sleep(min(2, remaining))
                remaining -= 2
                continue
            raw = response.model_dump(mode="json")
            try:
                trace.response(call_id, raw)
            except ValueError as error:
                raise RuntimeError(
                    "Unknown model usage: stop before spending more"
                ) from error
            if not response.choices:
                raise ValueError("Empty model response")
            choice = response.choices[0]
            if choice.finish_reason == "length":
                raise ValueError(
                    "Output truncated: split edits into smaller files/actions"
                )
            if getattr(choice.message, "refusal", None):
                raise ValueError("Model refused the coding request")
            content = choice.message.content
            if not content:
                raise ValueError("Empty model content")
            return parse_action(content), content
        raise RuntimeError("Unreachable retry state")
