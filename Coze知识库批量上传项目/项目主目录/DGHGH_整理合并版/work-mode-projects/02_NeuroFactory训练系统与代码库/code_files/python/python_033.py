# ========== AIDatasetPack Pro ==========
import os
import sys
import zipfile
import hashlib
import fnmatch
import json
import shutil
import threading
import concurrent.futures
import time
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict

class FileMerger:
    def __init__(self):
        self.hash_cache = {}

    def get_file_hash(self, file_path: str, block_size=65536) -> str:
        if file_path in self.hash_cache:
            return self.hash_cache[file_path]
        sha = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(block_size), b''):
                sha.update(chunk)
        h = sha.hexdigest()
        self.hash_cache[file_path] = h
        return h

    def find_duplicates_by_content(self, directory: str, exclude_patterns=None) -> Dict:
        groups = defaultdict(list)
        for root, dirs, files in os.walk(directory):
            if exclude_patterns:
                dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(d, p) for p in exclude_patterns)]
                files = [f for f in files if not any(fnmatch.fnmatch(f, p) for p in exclude_patterns)]
            for f in files:
                path = os.path.join(root, f)
                ext = os.path.splitext(f)[1].lower()
                try:
                    h = self.get_file_hash(path)
                    groups[(ext, h)].append(path)
                except:
                    continue
        return {k: v for k, v in groups.items() if len(v) > 1}

    def deep_compare_files(self, file1: str, file2: str) -> Dict:
        result = {"identical": False, "similarity": 0.0, "diff_positions": []}
        if not os.path.exists(file1) or not os.path.exists(file2):
            return result
        size1 = os.path.getsize(file1)
        size2 = os.path.getsize(file2)
        if size1 != size2:
            result["similarity"] = min(size1, size2) / max(size1, size2)
        else:
            h1 = self.get_file_hash(file1)
            h2 = self.get_file_hash(file2)
            if h1 == h2:
                result["identical"] = True
                result["similarity"] = 1.0
                return result
            if size1 < 10 * 1024 * 1024:
                with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
                    b1 = f1.read()
                    b2 = f2.read()
                matches = sum(1 for a, b in zip(b1, b2) if a == b)
                result["similarity"] = matches / max(len(b1), len(b2))
                for i, (a, b) in enumerate(zip(b1, b2)):
                    if a != b and len(result["diff_positions"]) < 100:
                        result["diff_positions"].append((i, a, b))
            else:
                sample_size = 1024 * 1024
                with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
                    s1 = f1.read(sample_size)
                    s2 = f2.read(sample_size)
                matches = sum(1 for a, b in zip(s1, s2) if a == b)
                result["similarity"] = matches / sample_size
        return result

    def merge_duplicate_files(self, directory: str, output_dir: str = None, dry_run=False) -> Dict:
        if output_dir is None:
            output_dir = directory + "_merged"
        os.makedirs(output_dir, exist_ok=True)
        duplicates = self.find_duplicates_by_content(directory)
        stats = {"total_groups": len(duplicates), "files_merged": 0, "saved_bytes": 0, "details": []}
        for (ext, h), paths in duplicates.items():
            keep = paths[0]
            for dup in paths[1:]:
                stats["files_merged"] += 1
                stats["saved_bytes"] += os.path.getsize(dup)
                if not dry_run:
                    rel = os.path.relpath(keep, directory)
                    dst = os.path.join(output_dir, rel)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(keep, dst)
                    stats["details"].append({"kept": keep, "removed": dup})
        return stats

class AutoDatasetCompressor:
    def __init__(self, src_dir, output_zip, exclude_patterns=None, auto_merge=True, auto_compare=True, workers=8):
        self.src_dir = os.path.abspath(src_dir)
        self.output_zip = output_zip
        self.exclude = exclude_patterns or [".DS_Store", "Thumbs.db", "*.tmp", "*.log", "__pycache__"]
        self.auto_merge = auto_merge
        self.auto_compare = auto_compare
        self.workers = workers
        self.merger = FileMerger()
        self.file_count = 0
        self.total_size = 0
        self.merged_stats = {}
        self.compare_report = {}

    def _should_exclude(self, path):
        name = os.path.basename(path)
        return any(fnmatch.fnmatch(name, p) for p in self.exclude)

    def _collect_files(self, directory):
        file_list = []
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not self._should_exclude(d)]
            for f in files:
                if self._should_exclude(f):
                    continue
                full = os.path.join(root, f)
                arc = os.path.relpath(full, directory)
                file_list.append((full, arc))
        return file_list

    def compress(self):
        print("="*70)
        print("🚀 AIDatasetPack Pro 全自动处理启动")
        print("="*70)

        work_dir = self.src_dir
        if self.auto_merge:
            print("🔍 阶段1：扫描相同后缀重复文件...")
            dup = self.merger.find_duplicates_by_content(self.src_dir, self.exclude)
            if dup:
                print(f"发现 {len(dup)} 组重复文件，开始合并...")
                self.merged_stats = self.merger.merge_duplicate_files(self.src_dir, dry_run=False)
                print(f"✅ 合并完成：合并 {self.merged_stats['files_merged']} 个文件，节省 {self.merged_stats['saved_bytes']//1024} KB")
                work_dir = self.src_dir + "_merged"
                if not os.path.exists(work_dir):
                    shutil.copytree(self.src_dir, work_dir, ignore=shutil.ignore_patterns(*self.exclude))
                self.src_dir = work_dir
            else:
                print("未发现重复文件，跳过合并")

        if self.auto_compare:
            print("🔬 阶段2：执行深度内容对比（抽样检查）...")
            all_files = self._collect_files(self.src_dir)
            sample = random.sample(all_files, min(50, len(all_files)))
            self.compare_report = {"checked": 0, "identical_pairs": 0, "similarity_avg": 0}
            sim_sum = 0
            for i, (f1, _) in enumerate(sample):
                for j, (f2, _) in enumerate(sample[i+1:], i+1):
                    if j >= len(sample): break
                    res = self.merger.deep_compare_files(f1, f2)
                    if res["identical"]:
                        self.compare_report["identical_pairs"] += 1
                    sim_sum += res["similarity"]
                    self.compare_report["checked"] += 1
            if self.compare_report["checked"]:
                self.compare_report["similarity_avg"] = sim_sum / self.compare_report["checked"]
            print(f"对比完成：检查 {self.compare_report['checked']} 对，平均相似度 {self.compare_report['similarity_avg']:.2f}")

        print("📦 阶段3：收集文件列表...")
        file_list = self._collect_files(self.src_dir)
        self.file_count = len(file_list)
        for fp, _ in file_list:
            self.total_size += os.path.getsize(fp)
        print(f"总计 {self.file_count} 个文件，原始大小 {self.total_size//(1024**2)} MB")

        print("🗜️ 阶段4：智能压缩中...")
        with zipfile.ZipFile(self.output_zip, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zipf:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as executor:
                futures = []
                for fp, arc in file_list:
                    futures.append(executor.submit(zipf.write, fp, arc))
                for i, fut in enumerate(concurrent.futures.as_completed(futures)):
                    if i % 100 == 0:
                        print(f"进度: {i}/{self.file_count}")
                    fut.result()

        print("📝 阶段5：生成元数据和校验...")
        meta = {
            "dataset": os.path.basename(self.src_dir),
            "created": datetime.now().isoformat(),
            "total_files": self.file_count,
            "total_size_mb": round(self.total_size/(1024**2),2),
            "auto_merged": self.merged_stats,
            "content_comparison": self.compare_report,
            "compression": "DEFLATED",
            "tool": "AIDatasetPack Pro v5.0"
        }
        with zipfile.ZipFile(self.output_zip, 'a') as zipf:
            zipf.writestr("dataset_meta.json", json.dumps(meta, indent=2))
        sha = hashlib.sha256()
        with open(self.output_zip, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha.update(chunk)
        with open(self.output_zip + ".sha256", 'w') as f:
            f.write(f"{sha.hexdigest()}  {os.path.basename(self.output_zip)}")

        print("="*70)
        print(f"✅ 全自动处理完成！输出: {self.output_zip}")
        print(f"   压缩后大小: {os.path.getsize(self.output_zip)//(1024**2)} MB")
        print(f"   节省空间: {self.merged_stats.get('saved_bytes',0)//(1024**2)} MB")
        print("="*70)

# ========== PyTorch 数据集集成 ==========
try:
    import torch
    from torch.utils.data import Dataset
    from PIL import Image
    class ZipImageDataset(Dataset):
        def __init__(self, zip_path, transform=None):
            self.zip = zipfile.ZipFile(zip_path)
            self.files = [f for f in self.zip.namelist() if f.lower().endswith(('.jpg','.png','.jpeg'))]
            self.transform = transform
        def __len__(self):
            return len(self.files)
        def __getitem__(self, idx):
            with self.zip.open(self.files[idx]) as f:
                img = Image.open(f).convert('RGB')
            if self.transform:
                img = self.transform(img)
            return img
    print("PyTorch 数据集加载器已就绪")
except:
    pass

# ========== 命令行入口 ==========
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AIDatasetPack Pro 全自动数据集打包")
    parser.add_argument("-i", "--input", required=True, help="源目录")
    parser.add_argument("-o", "--output", required=True, help="输出ZIP路径")
    parser.add_argument("--no-merge", action="store_true", help="禁用自动合并")
    parser.add_argument("--no-compare", action="store_true", help="禁用内容对比")
    parser.add_argument("-w", "--workers", type=int, default=8, help="线程数")
    args = parser.parse_args()

    compressor = AutoDatasetCompressor(
        src_dir=args.input,
        output_zip=args.output,
        auto_merge=not args.no_merge,
        auto_compare=not args.no_compare,
        workers=args.workers
    )
    compressor.compress()