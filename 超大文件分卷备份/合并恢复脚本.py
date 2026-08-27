# -*- coding: utf-8 -*-
"""
超大文件分卷合并恢复脚本
========================================
用途：把 GitHub 仓库 large-files-backup 分支中"超大文件分卷备份"里的分卷文件，
      一键合并还原成原始大文件（GitHub 单文件 100MB 上限导致原文件被切成分卷）。

用法（在本目录打开命令行执行）：
    python 合并恢复脚本.py [输出目录]

    不指定输出目录时，默认还原到本目录下（保持原相对路径结构）。

安全机制：
  1. 每一块分卷都会先校验 SHA256，任何一块损坏会立即报错，不会产出错误文件；
  2. 合并完成后再次校验整体大小与整体 SHA256，与原文件逐字节一致才算成功。
"""
import os
import sys
import json
import hashlib


def main():
    script = os.path.abspath(__file__)
    base = os.path.dirname(script)
    manifest_path = os.path.join(base, "_分卷清单.json")

    if not os.path.exists(manifest_path):
        print("错误：找不到 _分卷清单.json，请确认在本目录执行")
        sys.exit(1)

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    outdir = sys.argv[1] if len(sys.argv) > 1 else base
    outdir = os.path.abspath(outdir)
    all_ok = True
    restored = 0

    for entry in manifest:
        rel = entry["原文件相对路径"]
        # 分卷文件存放在：本目录/原相对路径所在目录/原文件名.partNNN
        if os.path.dirname(rel):
            part_dir = os.path.join(base, os.path.dirname(rel))
        else:
            part_dir = base
        target = os.path.join(outdir, rel)
        os.makedirs(os.path.dirname(target), exist_ok=True)

        size_mb = entry["原始大小字节"] / 1048576
        print(f"\n开始合并: {rel}（{entry['分卷数']} 块，原大小 {size_mb:.1f} MB）")

        gh = hashlib.sha256()
        total = 0
        bad = False
        with open(target, "wb") as out:
            for p in entry["分卷"]:
                pp = os.path.join(part_dir, p["文件名"])
                if not os.path.exists(pp):
                    print(f"  ✗ 缺少分卷: {p['文件名']}")
                    bad = True
                    break
                with open(pp, "rb") as f:
                    buf = f.read()
                if len(buf) != p["大小"] or hashlib.sha256(buf).hexdigest() != p["SHA256"]:
                    print(f"  ✗ 分卷校验失败(可能下载不完整): {p['文件名']}")
                    bad = True
                    break
                out.write(buf)
                gh.update(buf)
                total += len(buf)
                print(f"  ✓ {p['文件名']}（{p['大小'] / 1048576:.1f} MB）")

        if bad:
            all_ok = False
            try:
                os.remove(target)
            except OSError:
                pass
            continue

        if total == entry["原始大小字节"] and gh.hexdigest() == entry["原始SHA256"]:
            print(f"  ✓✓ 完整恢复且整体 SHA256 校验一致: {target}")
            restored += 1
        else:
            print(f"  ✗ 整体校验失败: {rel}（文件可能损坏）")
            all_ok = False

    print(f"\n完成：成功恢复 {restored}/{len(manifest)} 个文件")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
