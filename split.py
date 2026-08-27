# -*- coding: utf-8 -*-
"""
把一个大文件切成固定大小的分片，并生成 manifest.json（含原文件与每个分片的 sha256）。
用法:
  python split.py <源文件绝对路径> <基准目录绝对路径> <输出根目录绝对路径> [分片大小MB]
分片输出: <输出根目录>/<相对于基准目录的路径>.parts/part000, part001, ...
manifest: 同目录下 manifest.json
"""
import sys, os, hashlib, json, io

PART_MB = 80  # 默认分片 80MB（远低于 GitHub 100MB 硬限制）

def sha256_file(path, chunk=8 * 1024 * 1024):
    h = hashlib.sha256()
    with io.open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()

def main():
    if len(sys.argv) < 4:
        print("用法: python split.py <源文件> <基准目录> <输出根目录> [分片MB]")
        sys.exit(1)
    src = sys.argv[1]
    base = sys.argv[2].rstrip("\\/")
    outroot = sys.argv[3].rstrip("\\/")
    mb = int(sys.argv[4]) if len(sys.argv) > 4 else PART_MB
    part_size = mb * 1024 * 1024

    if not os.path.isfile(src):
        print("源文件不存在: %s" % src)
        sys.exit(2)

    rel = os.path.relpath(src, base).replace("\\", "/")
    parts_dir = os.path.join(outroot, rel + ".parts")
    os.makedirs(parts_dir, exist_ok=True)

    print("切片: %s" % rel)
    print("  分片目录: %s" % parts_dir)
    print("  分片大小: %d MB" % mb)

    total = os.path.getsize(src)
    file_hash = hashlib.sha256()
    parts = []
    idx = 0
    written = 0
    with io.open(src, "rb") as f:
        while True:
            chunk = f.read(part_size)
            if not chunk:
                break
            file_hash.update(chunk)
            part_name = "part%03d" % idx
            part_path = os.path.join(parts_dir, part_name)
            ph = hashlib.sha256()
            ph.update(chunk)
            with io.open(part_path, "wb") as pf:
                pf.write(chunk)
            ps = os.path.getsize(part_path)
            parts.append({"name": part_name, "size": ps, "sha256": ph.hexdigest()})
            written += ps
            idx += 1
            print("    %s  %.1f MB  sha256=%s..." % (part_name, ps / 1048576, ph.hexdigest()[:12]))

    manifest = {
        "original_rel_path": rel,
        "original_size": total,
        "original_sha256": file_hash.hexdigest(),
        "part_size": part_size,
        "part_count": len(parts),
        "parts": parts,
    }
    man_path = os.path.join(parts_dir, "manifest.json")
    with io.open(man_path, "w", encoding="utf-8") as mf:
        json.dump(manifest, mf, ensure_ascii=False, indent=2)

    print("完成: %d 个分片, 原文件 %.2f MB, sha256=%s" % (len(parts), total / 1048576, file_hash.hexdigest()))
    print("MANIFEST=%s" % man_path)
    # 校验写入字节数一致
    if written != total:
        print("警告: 写入字节 %d != 原大小 %d" % (written, total))
        sys.exit(3)
    print("BYTE_CHECK_OK")

if __name__ == "__main__":
    main()
