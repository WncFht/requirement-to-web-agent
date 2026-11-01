"""Real-app browser checks and executable E2E RED/GREEN gates."""

from hashlib import sha256
import os
from pathlib import Path
import re
from tempfile import TemporaryDirectory

from infrastructure.stages.frontend.interactions.e2e_runtime import RUNNER
from infrastructure.stages.frontend.ui.testing import (
    FrontendChecks,
    parse_playwright_result,
    require_green,
    require_red,
)
from infrastructure.shared.project.entrypoints import selected_path


def backend_cookie_names(output):
    """Expose literal cookie producers from the tested backend as bounded setup evidence."""
    names = set()
    for path in (output / "backend/src").rglob("*.ts"):
        source = path.read_text(encoding="utf-8-sig")
        constants = dict(
            re.findall(
                r"""const\s+(\w+)\s*=\s*["']([A-Za-z_][A-Za-z0-9_-]*)["']""", source
            )
        )
        for variable in re.findall(r"`\$\{(\w+)\}=\$\{", source):
            if variable in constants:
                names.add(constants[variable])
        names.update(re.findall(r"""[`"']([A-Za-z_][A-Za-z0-9_-]*)=\$\{""", source))
    return sorted(names)


def validate_e2e_source(source: str, cookie_names=None) -> None:
    """Reject known invalid E2E setup before freezing a generated test suite."""
    if re.search(r"https?://(?:localhost|127\.0\.0\.1)(?::\d+)?", source):
        raise ValueError(
            "The generated test hardcodes a loopback host. Use the baseURL fixture "
            "for Cookie.url and relative page.goto paths; the runner uses a random "
            "port on 127.0.0.1."
        )
    if (
        os.getenv("ARC_LEGACY_E2E_SOURCE_CHECK", "0") != "1"
        and "__ARC_UI_FIXTURE__" in source
    ):
        raise ValueError(
            "E2E tests cannot reference __ARC_UI_FIXTURE__. It is reserved for "
            "compiler-owned UI presence tests. Replace fixture injection with "
            "a real browser interaction scenario before this suite is frozen."
        )
    if not cookie_names or os.getenv("ARC_LEGACY_E2E_COOKIE_NAMES", "0") == "1":
        return
    tests = list(
        re.finditer(
            r"""\btest\(\s*(?:"((?:[^"\\]|\\.)*)"|'((?:[^'\\]|\\.)*)')""", source
        )
    )
    for index, match in enumerate(tests):
        title = (match.group(1) or match.group(2)).lower()
        if not re.search(r"\b(valid|existing|seeded)\s+session\b", title) or re.search(
            r"\b(invalid|unknown|unrecognized|expired|missing)\s+(session|cookie|credential)\b",
            title,
        ):
            continue
        body = source[
            match.end() : tests[index + 1].start()
            if index + 1 < len(tests)
            else len(source)
        ]
        for cookies in re.findall(r"\.addCookies\(\s*\[(.*?)\]\s*\)", body, re.DOTALL):
            names = re.findall(r"""\bname\s*:\s*["']([^"']+)["']""", cookies)
            if names and not set(names).intersection(cookie_names):
                raise ValueError(
                    f"Positive existing-session setup uses Cookie {names}, but tested backend producers use {cookie_names}. "
                    "Use the real backend cookie name with the seeded credential before freezing; do not change production handlers to accommodate this test."
                )


def test_path(rid, output=None):
    """Return a safe, stable E2E spec path for one requirement."""
    chosen = selected_path(output, "e2e_test", rid) if output is not None else None
    if chosen:
        return chosen
    slug = (
        rid
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", rid)
        else "requirement-" + sha256(rid.encode()).hexdigest()[:12]
    )
    return f"frontend/tests/e2e/{slug}.spec.ts"


def require_behavioral_red(result):
    """Require observable behavioral assertion failures and reject server, browser, or runtime failures."""
    try:
        require_red(result)
    except ValueError as error:
        raise ValueError(
            f"Expected behavioral assertion RED, not server/browser/runtime failure: {result}"
        ) from error


class E2EChecks(FrontendChecks):
    """Real-app Playwright checks with isolated test data ."""

    def __init__(self, output, maximum=5):
        """Reuse frontend checks with a longer real-server timeout and an enforced per-requirement test budget."""
        super().__init__(output, timeout=300)
        self.maximum = maximum

    def typecheck(self, files, full_source=True):
        """Compile UI and E2E tests, optionally restricting application sources during test generation."""
        return super().typecheck(
            files,
            test_roots=("frontend/tests/ui", "frontend/tests/e2e"),
            source_files=("src/**/*.ts", "src/**/*.tsx")
            if full_source
            else ("src/main.tsx",),
        )

    def tests(self, files):
        """Run only selected E2E specs with an owned temporary database, clean it up, ."""
        if not files:
            raise ValueError("Do not run empty E2E suites")
        for relative in files:
            if (
                not (self.output / relative)
                .resolve()
                .is_relative_to(self.output / "frontend/tests/e2e")
            ):
                raise ValueError("Run only the selected E2E test suites")
        # The Node runner creates a child directory here. Python also removes
        # it after timeout/interruption, so test databases never persist.
        with TemporaryDirectory(prefix="arc-e2e-owner-") as temporary:
            env = {**os.environ, "ARC_E2E_TEMP_ROOT": temporary}
            print(
                "Playwright E2E | real backend + isolated database | "
                + ", ".join(files),
                flush=True,
            )
            result = self.execute([RUNNER, *files], env=env)
        result = parse_playwright_result(result, include_files=True)
        return result
