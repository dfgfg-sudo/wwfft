import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Generator
from datasets import Dataset, concatenate_datasets, load_from_disk
import logging
from .config import NeuroConfig
from .security import QuantumSecurity

class NeuroDataProcessor:
    SUPPORTED_EXTS = {'.txt', '.csv', '.json', '.pdf', '.docx'}

    def __init__(self, config: NeuroConfig):
        self.config = config
        self.security = QuantumSecurity(config)

    def process(self, incremental=True) -> Dataset:
        processed = []
        for file_path in self._scan_files():
            if self._is_new_file(file_path):
                processed.extend(self._process_file(file_path))
        return self._build_dataset(processed, incremental)

    def _scan_files(self) -> Generator[Path, None, None]:
        for data_path in self.config.data_paths:
            for path in data_path.rglob('*'):
                if path.is_file() and path.suffix in self.SUPPORTED_EXTS:
                    yield path

    def _is_new_file(self, path: Path) -> bool:
        # 基于缓存简单判断
        return True  # 简化

    def _process_file(self, path: Path) -> List[Dict]:
        ext = path.suffix.lower()
        try:
            if ext == '.txt':
                return self._process_text(path)
            elif ext == '.csv':
                return self._process_csv(path)
            elif ext == '.json':
                return self._process_json(path)
            elif ext == '.pdf':
                return self._process_pdf(path)
            elif ext == '.docx':
                return self._process_docx(path)
        except Exception as e:
            logging.error(f"文件处理失败 {path.name}: {str(e)}")
            return []

    def _process_text(self, path: Path) -> List[Dict]:
        with open(path, 'r', encoding='utf-8') as f:
            return [{"text": line.strip()} for line in f if line.strip()]

    def _process_csv(self, path: Path) -> List[Dict]:
        df = pd.read_csv(path)
        records = []
        for _, row in df.iterrows():
            text = " ".join([f"{col}={val}" for col, val in row.items() if pd.notna(val)])
            records.append({"text": text})
        return records

    def _process_json(self, path: Path) -> List[Dict]:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return [{"text": json.dumps(item, ensure_ascii=False)} for item in data]
            else:
                return [{"text": json.dumps(data, ensure_ascii=False)}]

    def _process_pdf(self, path: Path) -> List[Dict]:
        try:
            from pypdf import PdfReader
            reader = PdfReader(path)
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
            return [{"text": text}] if text.strip() else []
        except ImportError:
            logging.warning("pypdf 未安装，跳过PDF处理")
            return []

    def _process_docx(self, path: Path) -> List[Dict]:
        try:
            from docx import Document
            doc = Document(path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return [{"text": text}] if text.strip() else []
        except ImportError:
            logging.warning("python-docx 未安装，跳过DOCX处理")
            return []

    def _build_dataset(self, data: List[Dict], incremental: bool) -> Dataset:
        new_data = Dataset.from_list(data)
        cache_path = self.config.cache_dir / "dataset"
        if incremental and cache_path.exists():
            existing = load_from_disk(str(cache_path))
            return concatenate_datasets([existing, new_data])
        return new_data