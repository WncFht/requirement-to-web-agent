"""Build a submission ZIP with a frozen source manifest."""

import json
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
from build_info import create_build_info, source_files


def package(root: Path, output: Path) -> dict:
    files = source_files(root)
    info = create_build_info(root, files)
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for name, data in files.items():
            entry = ZipInfo.from_file(root / name, name)
            entry.compress_type = ZIP_DEFLATED
            archive.writestr(entry, data)
        archive.writestr("build_info.json", json.dumps(info, ensure_ascii=False, indent=2) + "\n")
    return info


if __name__ == "__main__":
    output = root / "dist/mini_swe_arcbench_adapter.zip"
    info = package(root, output)
    print(json.dumps({"output": str(output), "commit": info["commit"], "tags": info["tags"],
                      "dirty": info["dirty"], "source_sha256": info["source_sha256"]}))
