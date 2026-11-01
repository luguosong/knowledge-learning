#!/usr/bin/env python3
"""在临时副本生成反向链接并严格构建，避免污染唯一正文。"""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from backlinks import run


ROOT = Path(__file__).resolve().parents[1]


def main():
    result = subprocess.run([sys.executable, str(ROOT / "工具/records.py"), "check"])
    if result.returncode:
        return result.returncode
    with tempfile.TemporaryDirectory(prefix="knowledge-build-") as temporary:
        stage = Path(temporary)
        shutil.copytree(ROOT / "docs", stage / "docs")
        shutil.copy2(ROOT / "zensical.toml", stage / "zensical.toml")
        print(f"backlinks: {run(stage / 'docs')} 个构建副本页面更新", flush=True)
        result = subprocess.run(["zensical", "build", "--clean", "--strict"], cwd=stage)
        if result.returncode:
            return result.returncode
        if (ROOT / "site").exists():
            shutil.rmtree(ROOT / "site")
        shutil.copytree(stage / "site", ROOT / "site", dirs_exist_ok=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
