# -*- coding: utf-8 -*-
"""
从分片目录恢复原始大文件（校验 sha256）。
用法:
  python merge_restore.py <某个 .parts 目录> [输出目录]
若不指定输出目录，则恢复到 .parts 同级（去掉 .parts 后缀）。
恢复后自动校验 sha256，不匹配会报错。
"""
import sys, os, hashlib, json, io

def main():
    if len(sys.argv) < 2:
        print("用法: python merge_restore.py <xxx.parts 目录> [输出目录]")
        sys.exit(1)
    parts_dir = sys.argv[1]
    man_path = os.path.join(parts_dir, "manifest.json")
    if not os.path.isfile(man_path):
        print("找不到 manifest: %s" % man_path)
        sys.exit(2)
    with io.open(man_path, encoding="utf-8") as f:
        m = json.load(f)

    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(parts_dir)
    out_path = os.path.join(out_dir, m["original_rel_path"])
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    h = hashlib.sha256()
    with io.open(out_path, "wb") as out:
        for p in m["parts"]:
            pp = os.path.join(parts_dir, p["name"])
            if not os.path.isfile(pp):
                print("缺失分片: %s" % pp)
                sys.exit(3)
            data = io.open(pp, "rb").read()
            # 校验单个分片
            ph = hashlib.sha256(data).hexdigest()
            if ph != p["sha256"]:
                print("分片 %s sha256 不匹配!" % p["name"])
                sys.exit(4)
            h.update(data)
            out.write(data)
    got = h.hexdigest()
    if got == m["original_sha256"]:
        print("恢复成功并校验通过: %s (%.2f MB)" % (out_path, os.path.getsize(out_path) / 1048576))
    else:
        print("校验失败! 期望 %s 实际 %s" % (m["original_sha256"], got))
        sys.exit(5)

if __name__ == "__main__":
    main()
