"""以乾淨 Git 專案驗證 docs/codex-jev 的交付；不讀金鑰、不呼叫外部服務。"""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


PACKAGE = Path(__file__).resolve().parents[2] / "docs/codex-jev"


def setup(root):
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    shutil.copytree(PACKAGE, root / "docs/codex-jev")


def run(root, *args, cwd=None):
    return subprocess.run(
        [sys.executable, str(root / "docs/codex-jev/install.py"), *args],
        cwd=cwd or root, capture_output=True, text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, timeout=10,
    )


def snapshot(root):
    paths = list((root / ".codex").rglob("*")) if (root / ".codex").exists() else []
    paths.append(root / ".gitignore")
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths if p.is_file()}


def test_clean_check_and_repeat():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp).resolve()
        setup(root)
        assert run(root, "--check").returncode == 0
        assert not (root / ".codex").exists()
        assert not (root / ".gitignore").exists()
        result = run(root)
        assert result.returncode == 0, result.stderr
        for source, destination in {
            "hooks.json": ".codex/hooks.json", "jev_router.py": ".codex/hooks/jev_router.py",
            "jev_light.toml": ".codex/agents/jev_light.toml",
        }.items():
            if source == "hooks.json":
                assert json.loads((root / destination).read_text())["hooks"] == json.loads((root / "docs/codex-jev" / source).read_text())["hooks"]
            else:
                assert (root / destination).read_bytes() == (root / "docs/codex-jev" / source).read_bytes()
        assert not (root / ".codex/jev-router/enabled").exists()
        before = snapshot(root)
        assert run(root).returncode == 0
        assert snapshot(root) == before


def test_merge_keeps_other_hooks_and_state():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp).resolve()
        setup(root)
        (root / ".codex/jev-router").mkdir(parents=True)
        (root / ".codex/jev-router/enabled").touch()
        other = {"hooks": [{"type": "command", "command": "echo existing"}]}
        old = {"description": "保留", "hooks": {"SessionStart": [other], "UserPromptSubmit": [other]}}
        (root / ".codex/hooks.json").write_text(json.dumps(old))
        assert run(root).returncode == 0
        merged = json.loads((root / ".codex/hooks.json").read_text())
        assert merged["description"] == old["description"]
        assert merged["hooks"]["SessionStart"] == [other]
        assert merged["hooks"]["UserPromptSubmit"][0] == other
        assert len(merged["hooks"]["UserPromptSubmit"]) == 2
        assert (root / ".codex/jev-router/enabled").is_file()
        assert run(root).returncode == 0
        assert json.loads((root / ".codex/hooks.json").read_text()) == merged


def test_failures_do_not_write():
    for scenario in ["missing_source", "invalid_json", "different_script", "different_hook", "symlink", "subdirectory"]:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            setup(root)
            (root / ".codex").mkdir()
            cwd = root
            if scenario == "missing_source":
                (root / "docs/codex-jev/jev_router.py").unlink()
            elif scenario == "invalid_json":
                (root / ".codex/hooks.json").write_text("not JSON")
            elif scenario == "different_script":
                (root / ".codex/hooks").mkdir()
                (root / ".codex/hooks/jev_router.py").write_text("# 保留既有版本\n")
            elif scenario == "different_hook":
                (root / ".codex/hooks.json").write_text(json.dumps({"hooks": {"UserPromptSubmit": [
                    {"hooks": [{"type": "command", "command": "python3 custom/jev_router.py"}]}
                ]}}))
            elif scenario == "symlink":
                (root / "outside").mkdir()
                (root / ".codex/hooks").symlink_to(root / "outside", target_is_directory=True)
            elif scenario == "subdirectory":
                cwd = root / "nested"
                cwd.mkdir()
            before = snapshot(root)
            result = run(root, cwd=cwd)
            assert result.returncode != 0, scenario
            assert snapshot(root) == before, scenario
            assert not (root / ".gitignore").exists(), scenario


if __name__ == "__main__":
    for test in [test_clean_check_and_repeat, test_merge_keeps_other_hooks_and_state, test_failures_do_not_write]:
        test()
        print("通過：" + test.__name__)
    print("乾淨安裝、合併、重複安裝及六種失敗情境均通過。")
