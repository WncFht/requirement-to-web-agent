import json
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from build_info import create_build_info, runtime_build_info
from scripts.package_agent import package


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def repository(tmp_path):
    root = tmp_path / "source"
    root.mkdir()
    (root / "main.py").write_text("print('example')\n")
    git(root, "init", "-q")
    git(root, "add", ".")
    git(root, "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
        "commit", "-qm", "initial")
    git(root, "tag", "mini-test")
    git(root, "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
        "tag", "-a", "mini-annotated", "-m", "release")
    return root


def test_packaged_identity_survives_missing_git_and_detects_changes(tmp_path):
    root = repository(tmp_path)
    output = tmp_path / "agent.zip"
    expected = package(root, output)
    assert expected["commit"] == git(root, "rev-parse", "HEAD")
    assert expected["tags"] == ["mini-annotated", "mini-test"]
    assert expected["dirty"] is False
    deployed = tmp_path / "deployed"
    with ZipFile(output) as archive:
        archive.extractall(deployed)
    info = runtime_build_info(deployed)
    assert info["origin"] == "package" and info["matches_build"] is True
    assert info["commit"] == expected["commit"]
    (deployed / "main.py").write_text("print('changed')\n")
    info = runtime_build_info(deployed)
    assert info["matches_build"] is False
    assert info["changed_files"] == ["main.py"]
    assert info["runtime_source_sha256"] != info["source_sha256"]
    (deployed / "main.py").unlink()
    assert runtime_build_info(deployed)["changed_files"] == ["main.py"]


def test_dirty_and_untracked_sources_are_not_reported_as_tagged_release(tmp_path):
    root = repository(tmp_path)
    original = create_build_info(root)
    (root / "main.py").write_text("print('edited')\n")
    changed = create_build_info(root)
    assert changed["dirty"] is True
    assert changed["commit"] == original["commit"]
    assert changed["source_sha256"] != original["source_sha256"]
    git(root, "checkout", "--", "main.py")
    (root / "build_info.py").write_text("# untracked source\n")
    assert create_build_info(root)["dirty"] is True


def test_only_shipped_files_affect_identity_and_no_parent_git_is_inherited(tmp_path):
    root = repository(tmp_path)
    initial = create_build_info(root)
    (root / ".env").write_text("SECRET=do-not-package")
    (root / "results").mkdir()
    (root / "results" / "large.zip").write_bytes(b"archive")
    info = create_build_info(root)
    assert info["dirty"] is False
    assert info["source_sha256"] == initial["source_sha256"]
    nested = root / "deployed"
    nested.mkdir()
    (nested / "main.py").write_text("print('no provenance')\n")
    unknown = runtime_build_info(nested)
    assert unknown["commit"] is None and unknown["dirty"] is None
    assert unknown["origin"] == "unversioned"


def test_repository_package_runs_without_git_and_writes_identity(tmp_path):
    archive_path = tmp_path / "agent.zip"
    expected = package(ROOT, archive_path)
    deployed = tmp_path / "deployed"
    with ZipFile(archive_path) as archive:
        assert "build_info.py" in archive.namelist()
        assert not any(name.startswith("results/") or name == ".env" for name in archive.namelist())
        archive.extractall(deployed)
    requirement = tmp_path / "task"
    requirement.mkdir()
    (requirement / "requirements.yaml").write_text("id: ROOT\nname: Example\nchildren: []\n")
    output = tmp_path / "application"
    process = subprocess.run(
        [sys.executable, str(deployed / "main.py"), str(requirement), "-o", str(output), "--dry-run"],
        capture_output=True, text=True, timeout=30,
    )
    assert process.returncode == 0, process.stderr
    info = json.loads((output / ".arc_adapter/build_info.json").read_text())
    assert info["matches_build"] is True
    assert info["source_sha256"] == expected["source_sha256"]
    event = next(json.loads(line) for line in process.stdout.splitlines()
                 if '"event": "build_info"' in line)
    assert event["commit"] == expected["commit"]
    assert event["source_sha256"] == expected["source_sha256"]
