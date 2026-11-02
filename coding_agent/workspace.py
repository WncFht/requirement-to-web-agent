"""Scoped reads and atomic, hash-checked exact edits across an entire application."""

import base64
import difflib
import hashlib
import mimetypes
import re
from pathlib import Path

from coding_agent.support.utils.paths import check_path_case, relative_path

from coding_agent.trace import sha

PROTECTED = {
    "backend/src/app.ts",
    "backend/src/server.ts",
    "backend/src/db/client.ts",
    "backend/src/db/setup.ts",
    "backend/src/api/types.ts",
    "frontend/src/main.tsx",
}
TEST_FILES = {
    "backend/tests/contract.test.ts",
    "frontend/tests/ui/presence.spec.ts",
    "frontend/tests/e2e/workflows.spec.ts",
}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


class Workspace:
    def __init__(self, output, inputs, trace=None):
        self.output, self.inputs = Path(output).resolve(), Path(inputs).resolve()
        self.trace = trace
        self.frozen = False

    def path(self, relative, *, input_file=False, diagnostic=False):
        relative_path(relative)
        root = self.inputs if input_file else self.output
        check_path_case(root, relative)
        parts = relative_path(relative).parts
        browser_diagnostic = (
            diagnostic
            and not input_file
            and len(parts) >= 5
            and parts[:3] == (".arc", "agent", "artifacts")
            and parts[3].startswith("browser-")
            and parts[-1] in {"error-context.md", "test-failed-1.png"}
        )
        current = root
        for index, part in enumerate(parts):
            if (
                part.startswith(".") and not (browser_diagnostic and index == 0)
            ) or part in {
                "node_modules",
                "data",
                "dist",
                "test-results",
            }:
                raise ValueError(f"Not an accessible source path: {relative}")
            current = current / part
            if current.is_symlink():
                raise ValueError(f"Symlink rejected: {relative}")
        if not current.resolve().is_relative_to(root) or current.is_dir():
            raise ValueError(f"Not a source file: {relative}")
        return current

    def inventory(self):
        paths = []
        for directory in (
            "backend/src",
            "frontend/src",
            "backend/tests",
            "frontend/tests",
            "frontend/public/assets",
        ):
            for path in sorted((self.output / directory).rglob("*")):
                if path.is_file() and not path.is_symlink():
                    paths.append(path.relative_to(self.output).as_posix())
        return paths

    def read(self, paths, start=1, limit=180):
        result = []
        if len(paths) > 12:
            raise ValueError("Read at most 12 paths per action")
        if (
            type(start) is not int
            or type(limit) is not int
            or start < 1
            or not 1 <= limit <= 400
        ):
            raise ValueError("Read needs start>=1 and 1<=limit<=400")
        for supplied in paths[:12]:
            is_input = supplied.startswith("input/")
            relative = supplied[6:] if is_input else supplied
            path = self.path(relative, input_file=is_input, diagnostic=True)
            if not path.is_file():
                raise ValueError(f"No such file: {supplied}")
            mime = mimetypes.guess_type(path.name)[0] or ""
            if mime.startswith("image/"):
                result.append(
                    {
                        "path": supplied,
                        "sha256": sha(path),
                        "image": {
                            "type": "image_url",
                            "image_url": {
                                "url": "data:"
                                + mime
                                + ";base64,"
                                + base64.b64encode(path.read_bytes()).decode()
                            },
                        },
                    }
                )
            else:
                lines = path.read_text(encoding="utf-8-sig").splitlines()
                selected = lines[start - 1 : start - 1 + limit]
                result.append(
                    {
                        "path": supplied,
                        "sha256": sha(path),
                        "start": start,
                        "total_lines": len(lines),
                        "omitted_lines": len(lines) - len(selected),
                        "content": "\n".join(
                            f"{i}: {s}" for i, s in enumerate(selected, start)
                        ),
                    }
                )
        return result

    def search(self, query):
        if not query or len(query) > 300:
            raise ValueError("Search query must have 1..300 characters")
        matches = []
        for relative in self.inventory():
            if Path(relative).suffix.lower() in IMAGE_SUFFIXES:
                continue
            path = self.path(relative)
            for line, content in enumerate(
                path.read_text(encoding="utf-8-sig").splitlines(), 1
            ):
                if query.lower() in content.lower():
                    matches.append(
                        {"path": relative, "line": line, "text": content[:700]}
                    )
        return {"matches": matches[:50], "omitted_matches": max(0, len(matches) - 50)}

    def writable(self, relative):
        if relative.startswith("frontend/public/assets/"):
            return self.frozen and Path(relative).suffix.lower() in IMAGE_SUFFIXES
        if relative in TEST_FILES:
            return not self.frozen
        if relative == "APP_CONTRACT.md":
            return True
        if relative in PROTECTED or not relative.startswith(
            ("backend/src/", "frontend/src/")
        ):
            return False
        if not self.frozen:
            return relative == "backend/src/db/initialize.ts" or relative.startswith(
                "backend/src/db/tables/"
            )
        return relative.endswith((".ts", ".tsx", ".css", ".sql"))

    def apply(self, edits):
        staged, originals, image_sources = {}, {}, {}
        for edit in edits:
            if not isinstance(edit, dict) or not isinstance(edit.get("path"), str):
                raise ValueError("Each edit needs path")
            relative = edit["path"]
            path = self.path(relative)
            if not self.writable(relative):
                raise ValueError(f"Protected edit in current phase: {relative}")
            before = path.read_bytes() if path.exists() else None
            image_asset = relative.startswith("frontend/public/assets/")
            if image_asset:
                source = edit.get("copy_from")
                if not isinstance(source, str) or not source.startswith("input/"):
                    raise ValueError("Image assets need copy_from=input/<image>")
                if before is not None or relative in staged:
                    raise ValueError(
                        "Copy images to a new asset path; existing assets are immutable"
                    )
                source_path = self.path(source[6:], input_file=True)
                if (
                    source_path.suffix.lower() not in IMAGE_SUFFIXES
                    or source_path.suffix.lower() != path.suffix.lower()
                    or not source_path.is_file()
                    or source_path.stat().st_size > 12_000_000
                ):
                    raise ValueError(
                        "Copy an input raster image of the same format, at most 12MB"
                    )
                after = source_path.read_bytes()
                image_sources[relative] = source
            elif "content" in edit:
                if (
                    relative in staged
                    or before is not None
                    or not isinstance(edit["content"], str)
                ):
                    raise ValueError(
                        "content creates a new file only; existing files need exact replacement"
                    )
                after = edit["content"]
            else:
                if before is None or sha(path) != edit.get("expected_sha256"):
                    raise ValueError(
                        f"Stale/missing file hash: {relative}; read the file again"
                    )
                old, new = edit.get("old_text"), edit.get("new_text")
                text = staged.get(relative, before.decode("utf-8-sig"))
                if (
                    not isinstance(old, str)
                    or not old
                    or not isinstance(new, str)
                    or text.count(old) != 1
                ):
                    raise ValueError(f"Old text must match exactly once: {relative}")
                after = text.replace(old, new, 1)
            if isinstance(after, str) and len(after.encode()) > 300_000:
                raise ValueError("Split source files larger than 300KB")
            if relative == "frontend/src/style.css" and not re.search(
                r"@import\s+['\"]tailwindcss['\"]\s*;", after
            ):
                raise ValueError(
                    "Preserve the Tailwind import in frontend/src/style.css"
                )
            originals[relative] = before
            staged[relative] = after
        written = []
        try:
            for relative, content in staged.items():
                path = self.path(relative)
                path.parent.mkdir(parents=True, exist_ok=True)
                written.append(relative)
                if isinstance(content, bytes):
                    path.write_bytes(content)
                else:
                    path.write_text(content)
        except (OSError, ValueError):
            for relative in reversed(written):
                path = self.path(relative)
                if originals[relative] is None:
                    path.unlink(missing_ok=True)
                else:
                    path.write_bytes(originals[relative])
            raise
        result = []
        for relative in staged:
            before = (
                (originals[relative] or b"").decode("utf-8-sig")
                if relative not in image_sources
                else ""
            )
            record = {
                "path": relative,
                "before_sha256": hashlib.sha256(originals[relative]).hexdigest()
                if originals[relative] is not None
                else None,
                "after_sha256": sha(self.path(relative)),
                "diff": (
                    "Copied immutable input image: " + image_sources[relative]
                    if relative in image_sources
                    else "".join(
                        difflib.unified_diff(
                            before.splitlines(True),
                            staged[relative].splitlines(True),
                            fromfile=relative,
                            tofile=relative,
                        )
                    )
                ),
            }
            result.append(record)
        if self.trace:
            self.trace.emit(
                "workspace.edit", artifact=self.trace.artifact("edits", result)
            )
        return result
