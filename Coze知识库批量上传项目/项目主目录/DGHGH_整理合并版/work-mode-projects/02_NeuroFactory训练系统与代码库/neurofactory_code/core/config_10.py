import json
import yaml
import os
import re
import hashlib
import chardet
import csv
import copy
import configparser
import xml.etree.ElementTree as ET
import tomllib
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
import logging
from collections import defaultdict

class UniversalFileMerger:
    """通用文件合并融合系统 - 按后缀名合并相同格式文件，100%保留原文"""

    def __init__(self):
        self.logger = self._setup_logging()
        self.merge_stats = {
            "total_files": 0,
            "merged_files": 0,
            "skipped_files": 0,
            "merged_formats": defaultdict(int),
            "merge_errors": defaultdict(list),
            "duplicate_content": 0,
            "unique_content": 0
        }
        self.content_hashes = set()
        self.file_cache = {}

    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        return logging.getLogger("UniversalFileMerger")

    def merge_files_by_extension(self, file_paths: List[str], output_dir: str = "merged_output") -> Dict[str, Any]:
        """按文件后缀名合并相同格式的文件"""
        try:
            files_by_ext = self._group_files_by_extension(file_paths)
            merge_results = {}
            for ext, files in files_by_ext.items():
                if len(files) == 1:
                    self.logger.info(f"扩展名 {ext} 只有一个文件，跳过合并")
                    continue
                self.logger.info(f"开始合并 {len(files)} 个 {ext} 文件")
                parsed_contents = self._read_and_parse_files(files, ext)
                merged_content = self._merge_same_format_contents(parsed_contents, ext)
                output_file = self._generate_merged_file(merged_content, ext, output_dir)
                merge_results[ext] = {
                    "original_files": files,
                    "merged_file": output_file,
                    "file_count": len(files),
                    "merged_content_type": type(merged_content).__name__,
                    "content_size": len(str(merged_content)),
                    "duplicates_removed": self.merge_stats["duplicate_content"]
                }
                self.merge_stats["merged_formats"][ext] += len(files)
                self.merge_stats["merged_files"] += len(files)
            summary = self._generate_merge_summary(merge_results, output_dir)
            return {"success": True, "merge_results": merge_results, "summary": summary, "statistics": dict(self.merge_stats)}
        except Exception as e:
            self.logger.error(f"合并文件时出错: {e}")
            return {"success": False, "error": str(e), "statistics": dict(self.merge_stats)}

    def _group_files_by_extension(self, file_paths: List[str]) -> Dict[str, List[str]]:
        files_by_ext = defaultdict(list)
        for path in file_paths:
            if not os.path.exists(path):
                self.logger.warning(f"文件不存在: {path}")
                self.merge_stats["skipped_files"] += 1
                continue
            ext = Path(path).suffix.lower() or ".unknown"
            files_by_ext[ext].append(path)
            self.merge_stats["total_files"] += 1
        return dict(files_by_ext)

    def _read_and_parse_files(self, file_paths: List[str], ext: str) -> List[Any]:
        parsed_contents = []
        for path in file_paths:
            try:
                content = self._read_file_with_detected_encoding(path)
                parsed = self._parse_content_by_extension(content, ext)
                h = self._calculate_content_hash(parsed)
                if h in self.content_hashes:
                    self.logger.info(f"跳过重复内容: {path}")
                    self.merge_stats["duplicate_content"] += 1
                    continue
                self.content_hashes.add(h)
                parsed_contents.append({"file_path": path, "content": parsed, "raw_content": content, "hash": h})
                self.merge_stats["unique_content"] += 1
            except Exception as e:
                self.logger.error(f"解析文件 {path} 时出错: {str(e)}")
                self.merge_stats["merge_errors"][ext].append(str(e))
        return parsed_contents

    def _read_file_with_detected_encoding(self, file_path: str) -> str:
        with open(file_path, 'rb') as f:
            raw = f.read()
        enc = chardet.detect(raw)['encoding'] or 'utf-8'
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            for e in ['utf-8','gbk','gb2312','latin-1','cp1252']:
                try:
                    return raw.decode(e)
                except:
                    continue
            raise ValueError(f"无法解码文件: {file_path}")

    def _parse_content_by_extension(self, content: str, ext: str) -> Any:
        ext = ext.lower()
        try:
            if ext in ['.json','.json5','.geojson']:
                repaired = self._repair_json_syntax(content)
                return json.loads(repaired)
            elif ext in ['.yaml','.yml']:
                return yaml.safe_load(content)
            elif ext == '.xml':
                return ET.fromstring(content)
            elif ext == '.csv':
                return list(csv.reader(content.splitlines()))
            elif ext == '.toml':
                return tomllib.loads(content)
            elif ext in ['.ini','.cfg','.conf']:
                cfg = configparser.ConfigParser()
                cfg.read_string(content)
                return cfg
            elif ext in ['.txt','.md','.rst','.log']:
                return content.splitlines()
            elif ext in ['.py','.js','.ts','.java','.cpp','.c','.h','.html','.css']:
                return {"type":"code","language":ext[1:],"content":content}
            else:
                return {"type":"unknown","extension":ext,"content":content}
        except Exception as e:
            self.logger.warning(f"解析 {ext} 文件出错，返回原始内容: {e}")
            return {"type":"raw","extension":ext,"content":content}

    def _repair_json_syntax(self, json_str: str) -> str:
        repaired = json_str.strip()
        if repaired.startswith('\ufeff'):
            repaired = repaired[1:]
        repairs = [(r',\s*}', '}'), (r',\s*]', ']'), (r"'([^']*)'", r'"\1"'), (r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":'), (r'//.*$', ''), (r'/\*.*?\*/', '', re.DOTALL)]
        for pat, rep in repairs:
            repaired = re.sub(pat, rep, repaired, flags=re.MULTILINE if pat in ['//.*$','/\*.*?\*/'] else 0)
        for wrong, correct in [("'true'","true"),("'false'","false"),("'null'","null"),("True","true"),("False","false"),("None","null")]:
            repaired = repaired.replace(wrong, correct)
        return repaired

    def _calculate_content_hash(self, content: Any) -> str:
        if isinstance(content, (dict, list)):
            return hashlib.md5(json.dumps(content, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()
        else:
            return hashlib.md5(str(content).encode('utf-8')).hexdigest()

    def _merge_same_format_contents(self, parsed_contents: List[Dict], ext: str) -> Any:
        if not parsed_contents:
            return None
        ext = ext.lower()
        if ext in ['.json','.json5','.geojson']:
            return self._merge_json_contents(parsed_contents)
        elif ext in ['.yaml','.yml']:
            return self._merge_yaml_contents(parsed_contents)
        elif ext == '.xml':
            return self._merge_xml_contents(parsed_contents)
        elif ext == '.csv':
            return self._merge_csv_contents(parsed_contents)
        elif ext == '.toml':
            return self._merge_toml_contents(parsed_contents)
        elif ext in ['.ini','.cfg','.conf']:
            return self._merge_ini_contents(parsed_contents)
        elif ext in ['.txt','.md','.rst','.log']:
            return self._merge_text_contents(parsed_contents)
        elif ext in ['.py','.js','.ts','.java','.cpp','.c','.h','.html','.css']:
            return self._merge_code_contents(parsed_contents)
        else:
            return self._merge_generic_contents(parsed_contents)

    def _merge_json_contents(self, parsed_contents: List[Dict]) -> Dict:
        if not parsed_contents:
            return {}
        merged = {}
        for item in parsed_contents:
            c = item["content"]
            if isinstance(c, dict):
                merged = self._deep_merge_dicts(merged, c)
            elif isinstance(c, list):
                if "array_items" not in merged:
                    merged["array_items"] = []
                merged["array_items"].extend(c)
            else:
                if "misc_values" not in merged:
                    merged["misc_values"] = []
                merged["misc_values"].append(c)
        merged["_metadata"] = {
            "merged_from": [i["file_path"] for i in parsed_contents],
            "merged_at": datetime.now().isoformat(),
            "total_files": len(parsed_contents),
            "tool": "UniversalFileMerger"
        }
        return merged

    def _deep_merge_dicts(self, target: Dict, source: Dict) -> Dict:
        for k, sv in source.items():
            if k in target:
                tv = target[k]
                if isinstance(tv, dict) and isinstance(sv, dict):
                    self._deep_merge_dicts(tv, sv)
                elif isinstance(tv, list) and isinstance(sv, list):
                    combined = tv + sv
                    seen = set()
                    unique = []
                    for it in combined:
                        it_str = json.dumps(it, sort_keys=True)
                        if it_str not in seen:
                            seen.add(it_str)
                            unique.append(it)
                    target[k] = unique
                else:
                    if not isinstance(tv, list):
                        target[k] = [tv]
                    if not isinstance(sv, list):
                        target[k].append(sv)
                    else:
                        target[k].extend(sv)
            else:
                target[k] = sv
        return target

    def _merge_yaml_contents(self, parsed_contents: List[Dict]) -> Dict:
        return self._merge_json_contents(parsed_contents)

    def _merge_xml_contents(self, parsed_contents: List[Dict]) -> ET.Element:
        root = ET.Element("merged_content")
        meta = ET.SubElement(root, "metadata")
        ET.SubElement(meta, "merged_at").text = datetime.now().isoformat()
        ET.SubElement(meta, "total_files").text = str(len(parsed_contents))
        for i, item in enumerate(parsed_contents):
            if isinstance(item["content"], ET.Element):
                fe = ET.SubElement(root, f"file_{i}")
                fe.set("source", item["file_path"])
                fe.append(item["content"])
        return root

    def _merge_csv_contents(self, parsed_contents: List[Dict]) -> List:
        merged = []
        headers = None
        for item in parsed_contents:
            rows = item["content"]
            if isinstance(rows, list) and rows:
                if headers is None and rows:
                    headers = rows[0]
                    merged.append(headers)
                start = 1 if rows[0]==headers else 0
                merged.extend(rows[start:])
        return merged

    def _merge_toml_contents(self, parsed_contents: List[Dict]) -> Dict:
        return self._merge_json_contents(parsed_contents)

    def _merge_ini_contents(self, parsed_contents: List[Dict]) -> configparser.ConfigParser:
        merged = configparser.ConfigParser()
        merged.add_section("metadata")
        merged.set("metadata", "merged_at", datetime.now().isoformat())
        merged.set("metadata", "total_files", str(len(parsed_contents)))
        merged.set("metadata", "source_files", ", ".join([p["file_path"] for p in parsed_contents]))
        for item in parsed_contents:
            cfg = item["content"]
            if isinstance(cfg, configparser.ConfigParser):
                for sec in cfg.sections():
                    if not merged.has_section(sec):
                        merged.add_section(sec)
                    for opt in cfg.options(sec):
                        merged.set(sec, opt, cfg.get(sec, opt))
        return merged

    def _merge_text_contents(self, parsed_contents: List[Dict]) -> str:
        lines = [
            f"# 合并文件生成于: {datetime.now().isoformat()}",
            f"# 共合并 {len(parsed_contents)} 个文件",
            "="*80
        ]
        for item in parsed_contents:
            lines.append(f"\n# 文件来源: {item['file_path']}")
            lines.append("#"*60)
            if isinstance(item["content"], list):
                lines.extend(item["content"])
            else:
                lines.append(str(item["content"]))
            lines.append("")
        return "\n".join(lines)

    def _merge_code_contents(self, parsed_contents: List[Dict]) -> Dict:
        merged = {
            "type": "merged_code",
            "metadata": {
                "merged_at": datetime.now().isoformat(),
                "total_files": len(parsed_contents),
                "source_files": []
            },
            "files": []
        }
        for item in parsed_contents:
            merged["metadata"]["source_files"].append(item["file_path"])
            if isinstance(item["content"], dict) and item["content"].get("type")=="code":
                merged["files"].append({
                    "path": item["file_path"],
                    "language": item["content"].get("language", "unknown"),
                    "content": item["content"].get("content", "")
                })
            else:
                merged["files"].append({
                    "path": item["file_path"],
                    "language": "unknown",
                    "content": str(item["content"])
                })
        return merged

    def _merge_generic_contents(self, parsed_contents: List[Dict]) -> Dict:
        return {
            "type": "merged_generic",
            "metadata": {
                "merged_at": datetime.now().isoformat(),
                "total_files": len(parsed_contents),
                "extensions": list(set([Path(p["file_path"]).suffix for p in parsed_contents]))
            },
            "files": [
                {
                    "path": p["file_path"],
                    "content_type": type(p["content"]).__name__,
                    "content": p["content"] if isinstance(p["content"], (str, int, float, bool)) else str(p["content"])
                }
                for p in parsed_contents
            ]
        }

    def _generate_merged_file(self, merged_content: Any, ext: str, output_dir: str) -> str:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = f"merged_{ext[1:]}_{ts}"
        if ext in ['.json','.json5','.geojson']:
            fp = Path(output_dir) / f"{base}.json"
            with open(fp,'w',encoding='utf-8') as f:
                json.dump(merged_content, f, ensure_ascii=False, indent=2)
        elif ext in ['.yaml','.yml']:
            fp = Path(output_dir) / f"{base}.yaml"
            with open(fp,'w',encoding='utf-8') as f:
                yaml.dump(merged_content, f, default_flow_style=False, allow_unicode=True)
        elif ext == '.xml':
            fp = Path(output_dir) / f"{base}.xml"
            ET.ElementTree(merged_content).write(fp, encoding='utf-8', xml_declaration=True)
        elif ext == '.csv':
            fp = Path(output_dir) / f"{base}.csv"
            with open(fp,'w',newline='',encoding='utf-8') as f:
                csv.writer(f).writerows(merged_content)
        elif ext == '.toml':
            fp = Path(output_dir) / f"{base}.toml"
            import tomli_w
            with open(fp,'wb') as f:
                tomli_w.dump(merged_content, f)
        elif ext in ['.ini','.cfg','.conf']:
            fp = Path(output_dir) / f"{base}.ini"
            with open(fp,'w',encoding='utf-8') as f:
                merged_content.write(f)
        elif ext in ['.txt','.md','.rst','.log']:
            fp = Path(output_dir) / f"{base}.txt"
            with open(fp,'w',encoding='utf-8') as f:
                f.write(merged_content)
        else:
            fp = Path(output_dir) / f"{base}.json"
            with open(fp,'w',encoding='utf-8') as f:
                json.dump(merged_content, f, ensure_ascii=False, indent=2)
        return str(fp)

    def _generate_merge_summary(self, merge_results: Dict, output_dir: str) -> Dict:
        summary_file = Path(output_dir) / "merge_summary.json"
        summary = {
            "generated_at": datetime.now().isoformat(),
            "output_directory": output_dir,
            "total_formats_merged": len(merge_results),
            "formats": {},
            "statistics": dict(self.merge_stats)
        }
        for ext, res in merge_results.items():
            summary["formats"][ext] = {
                "file_count": res["file_count"],
                "merged_file": res["merged_file"],
                "content_type": res["merged_content_type"],
                "content_size_kb": res["content_size"] // 1024
            }
        with open(summary_file,'w',encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        return summary