#!/usr/bin/env python3
"""file-notes: 记录文件和文件夹的用途和状态"""

import json, os, sys
from datetime import date
from pathlib import Path

DATA_DIR = Path.home() / ".file-notes"
DATA_FILE = DATA_DIR / "data.json"

STATUS = {"keep": "保留", "can_delete": "可清理", "unsure": "不确定", "archive": "已归档"}

def load():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text("utf-8"))
    return {"entries": []}

def save(data):
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), "utf-8")

def norm(p):
    return str(Path(p).resolve()).lower()

def find(data, needle):
    n = norm(needle)
    for e in data["entries"]:
        if e["normalized"] == n:
            return e
        # 如果 needle 是已记录路径的父目录，也匹配
        if n != e["normalized"] and (e["normalized"].startswith(n + os.sep) or n.startswith(e["normalized"] + os.sep)):
            return e
    return None

def show(entry):
    s = STATUS.get(entry.get("status", ""), "未标注")
    print(f"  路径: {entry['path']}")
    print(f"  状态: {s}")
    print(f"  描述: {entry.get('description', '(无)')}")
    if entry.get("tags"):
        print(f"  标签: {', '.join(entry['tags'])}")
    print(f"  记录于: {entry.get('updated_at', '?')}")

def cmd_lookup(path):
    data = load()
    e = find(data, path)
    if e:
        show(e)
    else:
        print(f"'{path}' 没有记录。")
        r = input("添加记录？[y/N] ").strip().lower()
        if r == "y":
            cmd_add(path)

def cmd_add(path, status=None, description=None, tags=None):
    data = load()
    e = find(data, path)
    if e:
        print("更新已有记录：")
        show(e)
    else:
        e = {"path": str(Path(path).resolve()), "normalized": norm(path)}
        data["entries"].append(e)
    if not status:
        # 有描述参数时不弹交互，默认 unsure
        if description:
            status = "unsure"
        else:
            print(f"\n状态选项: {', '.join(f'{k}={v}' for k,v in STATUS.items())}")
            s = input("状态 (默认 unsure): ").strip() or "unsure"
            status = s if s in STATUS else "unsure"
    e["status"] = status
    if not description:
        d = input("描述 (用途、备注等): ").strip()
        if d:
            description = d
    if description:
        e["description"] = description
    if tags:
        e["tags"] = tags
    e["updated_at"] = str(date.today())
    save(data)
    print(f"✅ 已保存")

def cmd_list(filter_status=None):
    data = load()
    if not data["entries"]:
        print("还没有任何记录。")
        return
    for e in data["entries"]:
        if filter_status and e.get("status") != filter_status:
            continue
        s = STATUS.get(e.get("status", ""), "未标注")
        print(f"[{s}] {e['path']}")

def cmd_review():
    """列出未标注和不确定的路径"""
    data = load()
    todo = [e for e in data["entries"] if e.get("status") in (None, "unsure", "")]
    if not todo:
        print("所有路径都已标注！ ✅")
        return
    print(f"还有 {len(todo)} 条待标注：\n")
    for e in todo:
        show(e)
        r = input("\n现在标注？[y/N] ").strip().lower()
        if r == "y":
            print(f"状态选项: {', '.join(f'{k}={v}' for k,v in STATUS.items())}")
            s = input("状态: ").strip()
            if s in STATUS:
                e["status"] = s
            d = input("描述: ").strip()
            if d:
                e["description"] = d
            e["updated_at"] = str(date.today())
            save(data)
            print("✅ 已更新\n")

def cmd_export():
    """导出所有记录为易读的文本"""
    data = load()
    lines = [f"文件笔记 — {date.today()}", "=" * 40, ""]
    for e in sorted(data["entries"], key=lambda x: x["path"]):
        s = STATUS.get(e.get("status", ""), "未标注")
        lines.append(f"[{s}] {e['path']}")
        if e.get("description"):
            lines.append(f"       {e['description']}")
        lines.append("")
    print("\n".join(lines))

def main():
    # Windows 终端 UTF-8 支持
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        print("用法:")
        print("  file-notes <路径>         查询/添加路径记录")
        print("  file-notes add <路径>      添加记录（交互式）")
        print("  file-notes add <路径> --desc <描述>  添加记录（非交互式）")
        print("  file-notes list            列出所有记录")
        print("  file-notes list <状态>     按状态筛选 (keep/can_delete/unsure/archive)")
        print("  file-notes review          审查待标注的路径")
        print("  file-notes export          导出记录")
        return

    cmd = sys.argv[1]
    if cmd in ("add", "a"):
        if len(sys.argv) < 3:
            print("请指定路径")
            return
        # 支持 --desc "描述" 非交互式添加
        desc = None
        args = sys.argv[3:]
        for i, a in enumerate(args):
            if a == "--desc" and i + 1 < len(args):
                desc = args[i + 1]
                break
        cmd_add(sys.argv[2], description=desc)
    elif cmd in ("list", "ls"):
        cmd_list(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == "review":
        cmd_review()
    elif cmd == "export":
        cmd_export()
    else:
        cmd_lookup(cmd)

if __name__ == "__main__":
    main()
