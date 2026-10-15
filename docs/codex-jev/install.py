#!/usr/bin/env python3
"""在 Git 根目錄安裝隨附的 Codex 設定；不設定金鑰、不信任 Hook、不開啟路由。"""

import argparse
import ast
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


FILES = {
    "jev_router.py": ".codex/hooks/jev_router.py",
    "jev_light.toml": ".codex/agents/jev_light.toml",
}


def merge_hooks(existing, bundled):
    if not isinstance(existing, dict):
        raise ValueError("既有 hooks.json 必須是 JSON object。")
    merged = copy.deepcopy(existing)
    events = merged.setdefault("hooks", {})
    if not isinstance(events, dict):
        raise ValueError("既有 hooks 欄位必須是 object。")
    groups = events.setdefault("UserPromptSubmit", [])
    if not isinstance(groups, list):
        raise ValueError("既有 UserPromptSubmit 必須是 array。")
    try:
        wanted_group = bundled["hooks"]["UserPromptSubmit"][0]
        wanted = wanted_group["hooks"][0]
    except (KeyError, IndexError, TypeError):
        raise ValueError("來源 hooks.json 缺少 Jev 的 UserPromptSubmit handler。") from None
    if not isinstance(wanted, dict) or "jev_router.py" not in str(wanted.get("command", "")):
        raise ValueError("來源 hooks.json 未指定 Jev 路由腳本。")
    matches = 0
    for group in groups:
        if not isinstance(group, dict) or not isinstance(group.get("hooks"), list):
            raise ValueError("既有 UserPromptSubmit 的群組格式無法安全合併。")
        for handler in group["hooks"]:
            if not isinstance(handler, dict):
                raise ValueError("既有 Hook handler 格式無法安全合併。")
            command = handler.get("command", "")
            if not isinstance(command, str):
                raise ValueError("既有 Hook command 必須是字串。")
            if "jev_router.py" in command:
                if handler != wanted:
                    raise ValueError("已有不同的 Jev Hook；請先比對，未覆蓋或重複註冊。")
                matches += 1
    if matches > 1:
        raise ValueError("已有重複的 Jev Hook；請先清理，未變更設定。")
    if not matches:
        groups.append(copy.deepcopy(wanted_group))
    return merged


def check_destination(path, root):
    current = path
    while current != root:
        if current.is_symlink():
            raise ValueError("安裝目標包含 symlink，請先確認實際位置：" + str(current.relative_to(root)))
        if current.exists() and current != path and not current.is_dir():
            raise ValueError("安裝目錄被一般檔案占用：" + str(current.relative_to(root)))
        current = current.parent
    if path.exists() and not path.is_file():
        raise ValueError("安裝目標不是一般檔案：" + str(path.relative_to(root)))


def plan_install(root, package):
    # 在任何寫入前，讀完並檢查所有來源與目標。
    sources = {}
    for name in ["hooks.json", *FILES]:
        path = package / name
        if not path.is_file() or path.is_symlink():
            raise ValueError("安裝來源缺少一般檔案：" + name)
        sources[name] = path.read_bytes()
    bundled = json.loads(sources["hooks.json"])
    ast.parse(sources["jev_router.py"].decode("utf-8"))
    changes = {}
    for name, relative in FILES.items():
        dest = root / relative
        check_destination(dest, root)
        if dest.exists() and dest.read_bytes() != sources[name]:
            raise ValueError("同名檔案內容不同，請先比對，未覆蓋：" + relative)
        if not dest.exists():
            changes[dest] = sources[name]
    hooks = root / ".codex/hooks.json"
    check_destination(hooks, root)
    existing = json.loads(hooks.read_text()) if hooks.exists() else {}
    merged = merge_hooks(existing, bundled)
    if not hooks.exists() or merged != existing:
        changes[hooks] = (json.dumps(merged, ensure_ascii=False, indent=2) + "\n").encode()
    ignore = root / ".gitignore"
    check_destination(ignore, root)
    old = ignore.read_text() if ignore.exists() else ""
    if ".codex/jev-router/" not in old.splitlines():
        changes[ignore] = (old + ("\n" if old and not old.endswith("\n") else "")
                           + ".codex/jev-router/\n").encode()
    return changes


def write_changes(changes):
    # 先準備所有檔案，確認可寫入後才逐一取代目標。
    staged = []
    try:
        for dest, data in changes.items():
            dest.parent.mkdir(parents=True, exist_ok=True)
            fd, name = tempfile.mkstemp(prefix=".jev-install-", dir=dest.parent)
            staged.append((Path(name), dest))
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
            os.chmod(name, dest.stat().st_mode & 0o777 if dest.exists() else 0o644)
        for temporary, dest in staged:
            os.replace(temporary, dest)
    finally:
        for temporary, _ in staged:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description="安裝 Codex × Jev；保留既有設定與開關")
    parser.add_argument("--check", action="store_true", help="只檢查安裝計畫，不寫入")
    args = parser.parse_args()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], check=True,
            capture_output=True, text=True,
        )
        root = Path(result.stdout.strip()).resolve()
        if Path.cwd().resolve() != root:
            raise ValueError("請切到 Git 專案根目錄再執行。")
        changes = plan_install(root, Path(__file__).resolve().parent)
        if not args.check:
            write_changes(changes)
        for path in changes:
            print(("預計更新：" if args.check else "已更新：") + str(path.relative_to(root)))
        if not changes:
            print("設定已一致，不需更新。")
        print("檢查完成，未寫入。" if args.check else "安裝完成；尚未設定金鑰、信任 Hook 或變更路由開關。")
        return 0
    except json.JSONDecodeError:
        print("安裝失敗：來源或既有 hooks.json 不是有效 JSON，未進行寫入。", file=sys.stderr)
        return 1
    except ValueError as error:
        print("安裝失敗：" + str(error), file=sys.stderr)
        return 1
    except (OSError, SyntaxError, subprocess.SubprocessError):
        print("安裝失敗：請確認 Git、來源 Python 語法與目標目錄讀寫權限；修正後重新執行。", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
