"""Export committed compiler history and a teacher-relative source patch."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def git(*arguments):
    return subprocess.check_output(["git", *arguments], cwd=ROOT)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT.parent)
    args = parser.parse_args()
    if git("status", "--porcelain").strip():
        parser.error("Commit source changes before exporting")
    output = args.output_dir.resolve()
    artifacts = output / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    patch = git(
        "diff",
        "--binary",
        "teacher-baseline",
        "HEAD",
        "--",
        "*.py",
        "pyproject.toml",
        "requirements.txt",
        "uv.lock",
        ":(exclude)scripts/**",
    )
    (output / "upstream.patch").write_bytes(patch)
    bundle = artifacts / "compiler-source.bundle"
    with tempfile.TemporaryDirectory(prefix="compiler-export-") as temporary:
        staged = Path(temporary) / bundle.name
        subprocess.run(
            ["git", "bundle", "create", str(staged), "--all"], cwd=ROOT, check=True
        )
        subprocess.run(
            ["git", "bundle", "verify", str(staged)],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
        bundle.write_bytes(staged.read_bytes())
    manifest = {
        "source_revision": git("rev-parse", "HEAD").decode().strip(),
        "baseline_revision": git("rev-parse", "teacher-baseline").decode().strip(),
        "bundle": "artifacts/compiler-source.bundle",
        "bundle_sha256": hashlib.sha256(bundle.read_bytes()).hexdigest(),
        "patch": "upstream.patch",
        "patch_sha256": hashlib.sha256(patch).hexdigest(),
        "restore": "git clone artifacts/compiler-source.bundle source",
        "scope": "All committed refs; no environment, credentials or ignored run outputs",
    }
    (artifacts / "compiler-export.json").write_text(
        json.dumps(manifest, indent=2) + "\n"
    )
    provenance = output / "source.json"
    if provenance.is_file():
        data = json.loads(provenance.read_text())
        checkpoint = subprocess.run(
            ["git", "describe", "--tags", "--exact-match", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        data.setdefault("compiler_history", {}).update(
            {
                "revision": manifest["source_revision"],
                "checkpoint": checkpoint.stdout.strip()
                if checkpoint.returncode == 0
                else None,
                "bundle": manifest["bundle"],
                "manifest": "artifacts/compiler-export.json",
            }
        )
        provenance.write_text(json.dumps(data, ensure_ascii=False, indent=4) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
