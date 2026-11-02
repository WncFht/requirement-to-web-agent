"""Immutable runtime settings; platform credentials never enter public records."""

from dataclasses import dataclass, field
import os
from pathlib import Path
from urllib.parse import urlsplit


@dataclass(frozen=True)
class Config:
    inputs: Path
    output: Path
    model: str = "deepseek-flash"
    base_url: str = ""
    api_key: str = field(default="", repr=False)
    max_turns: int = 100
    max_tokens: int = 2_500_000
    max_seconds: int = 1200
    output_tokens: int = 8192
    transport_retries: int = 1
    port: int = 3000

    @classmethod
    def environment(cls, inputs, output, port=3000):
        values = {}
        for name, default in (
            ("max_turns", 100),
            ("max_tokens", 2_500_000),
            ("max_seconds", 1200),
            ("output_tokens", 8192),
            ("transport_retries", 1),
        ):
            values[name] = int(os.getenv("ARC_AGENT_" + name.upper(), str(default)))
            if values[name] < (0 if name == "transport_retries" else 1):
                raise ValueError(f"Invalid coding-agent budget: {name}")
        result = cls(
            Path(inputs).resolve(),
            Path(output).resolve(),
            model=os.getenv("MODEL") or "deepseek-flash",
            base_url=os.environ.get("OPENAI_BASE_URL", ""),
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            port=port,
            **values,
        )
        if not result.base_url or not result.api_key:
            raise ValueError("OPENAI_BASE_URL and OPENAI_API_KEY must be injected")
        if not (result.inputs / "requirements.yaml").is_file():
            raise ValueError("The input directory must contain requirements.yaml")
        if result.output == result.inputs or result.output.is_relative_to(
            result.inputs
        ):
            raise ValueError("Output must be outside the input directory")
        return result

    def public(self):
        endpoint = urlsplit(self.base_url)
        return {
            "model": self.model,
            "endpoint": f"{endpoint.scheme}://{endpoint.hostname}{endpoint.path}",
            "max_turns": self.max_turns,
            "max_tokens": self.max_tokens,
            "max_seconds": self.max_seconds,
            "output_tokens": self.output_tokens,
            "transport_retries": self.transport_retries,
            "port": self.port,
        }
