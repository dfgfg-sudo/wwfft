import os
import pandas as pd
import glob
from PIL import Image
import zipfile
import json
import docx
import PyPDF2
import io

class DataHarvester:
    def __init__(self, base_path="C:\\Users\\Administrator\\Documents\\uytrertrt\\Bunny-v1_0-3B\\data"):
        self.base_path = base_path
        self.supported_extensions = {
            '.txt': self._read_text_file,
            '.csv': self._read_csv,
            '.xlsx': self._read_excel,
            '.json': self._read_json,
            '.docx': self._read_docx,
            '.jpg': self._read_image,
            '.png': self._read_image,
            '.pdf': self._read_pdf,
            '.zip': self._process_zip
        }
        self.data_store = {
            'text': [],
            'tabular': [],
            'images': [],
            'documents': []
        }

    def harvest_data(self):
        """主函数，搜索并处理所有支持的文件"""
        print(f"开始在 {self.base_path} 中搜索数据文件...")
        
        # 递归搜索所有支持的文件
        for ext in self.supported_extensions:
            file_pattern = os.path.join(self.base_path, '**', f'*{ext}')
            file_list = glob.glob(file_pattern, recursive=True)
            
            for file_path in file_list:
                try:
                    self._process_file(file_path)
                except Exception as e:
                    print(f"处理文件 {file_path} 时出错: {str(e)}")
        
        print("数据收集完成!")
        print(f"收集到 {len(self.data_store['text'])} 文本文件")
        print(f"收集到 {len(self.data_store['tabular'])} 表格文件")
        print(f"收集到 {len(self.data_store['images'])} 图像文件")
        print(f"收集到 {len(self.data_store['documents'])} 文档文件")
        
        return self.data_store

    def _process_file(self, file_path):
        """根据文件扩展名处理单个文件"""
        _, ext = os.path.splitext(file_path)
        if ext.lower() in self.supported_extensions:
            content = self.supported_extensions[ext.lower()](file_path)
            
            # 根据内容类型分类存储
            if ext.lower() in ['.txt', '.pdf', '.docx']:
                self.data_store['text'].append({
                    'file_path': file_path,
                    'content': content
                })
            elif ext.lower() in ['.csv', '.xlsx', '.json']:
                self.data_store['tabular'].append({
                    'file_path': file_path,
                    'content': content
                })
            elif ext.lower() in ['.jpg', '.png']:
                self.data_store['images'].append({
                    'file_path': file_path,
                    'content': content
                })
            elif ext.lower() == '.zip':
                # ZIP文件可能包含多种类型内容
                pass

    # 以下是各种文件类型的读取方法
    def _read_text_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _read_csv(self, file_path):
        return pd.read_csv(file_path)

    def _read_excel(self, file_path):
        return pd.read_excel(file_path)

    def _read_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _read_docx(self, file_path):
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])

    def _read_image(self, file_path):
        img = Image.open(file_path)
        return img

    def _read_pdf(self, file_path):
        text = ""
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text()
        return text

    def _process_zip(self, file_path):
        """处理ZIP文件，提取其中的内容"""
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                if not file_info.is_dir():
                    _, ext = os.path.splitext(file_info.filename)
                    if ext.lower() in self.supported_extensions:
                        try:
                            with zip_ref.open(file_info) as file:
                                if ext.lower() in ['.jpg', '.png']:
                                    content = Image.open(io.BytesIO(file.read()))
                                else:
                                    content = file.read().decode('utf-8')
                                
                                # 存储提取的内容
                                if ext.lower() in ['.txt', '.pdf', '.docx']:
                                    self.data_store['text'].append({
                                        'file_path': f"{file_path}/{file_info.filename}",
                                        'content': content
                                    })
                                elif ext.lower() in ['.csv', '.xlsx', '.json']:
                                    # 对于表格数据可能需要特殊处理
                                    pass
                                elif ext.low以下是一个完整的自动化解决方案，用于从指定目录及其子目录中搜索多种格式的原始数据文件，并进行处理以供模型训练、微调和推理使用：