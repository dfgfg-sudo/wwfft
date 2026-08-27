import os
import pandas as pd
import glob
import zipfile
import json
import docx
import PyPDF2
from PIL import Image
import io
import logging
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import numpy as np

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoDataFeeder:
    def __init__(self, base_path="C:\\Users\\Administrator\\Documents\\uytrertrt\\Bunny-v1_0-3B\\data"):
        self.base_path = base_path
        self.supported_extensions = {
            '.txt': self._process_text,
            '.csv': self._process_tabular,
            '.xlsx': self._process_tabular,
            '.json': self._process_json,
            '.docx': self._process_docx,
            '.jpg': self._process_image,
            '.png': self._process_image,
            '.pdf': self._process_pdf,
            '.zip': self._process_zip
        }
        self.data_pipeline = {
            'text': [],
            'tabular': [],
            'images': [],
            'metadata': []
        }
        self.data_stats = {
            'total_files': 0,
            'processed_files': 0,
            'failed_files': 0
        }

    def run_pipeline(self):
        """运行完整的数据处理管道"""
        logger.info("启动自动化数据采集和清洗管道...")
        
        # 阶段1：数据采集
        self._collect_data()
        
        # 阶段2：数据清洗
        self._clean_data()
        
        # 阶段3：数据投喂准备
        prepared_data = self._prepare_for_training()
        
        logger.info(f"管道完成。处理文件: {self.data_stats['processed_files']}/{self.data_stats['total_files']}")
        return prepared_data

    def _collect_data(self):
        """收集所有支持的文件类型数据"""
        logger.info(f"从 {self.base_path} 收集数据...")
        
        # 使用多线程加速文件收集
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for ext in self.supported_extensions:
                file_pattern = os.path.join(self.base_path, '**', f'*{ext}')
                file_list = glob.glob(file_pattern, recursive=True)
                self.data_stats['total_files'] += len(file_list)
                
                for file_path in file_list:
                    futures.append(executor.submit(self._process_file, file_path))
            
            # 使用tqdm显示进度条
            for future in tqdm(futures, desc="收集数据文件", unit="file"):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"文件处理失败: {str(e)}")
                    self.data_stats['failed_files'] += 1

    def _process_file(self, file_path):
        """处理单个文件"""
        try:
            _, ext = os.path.splitext(file_path)
            if ext.lower() in self.supported_extensions:
                processor = self.supported_extensions[ext.lower()]
                result = processor(file_path)
                
                if result:
                    data_type = self._determine_data_type(ext)
                    self.data_pipeline[data_type].append({
                        'file_path': file_path,
                        'raw_data': result,
                        'cleaned_data': None,
                        'status': 'raw'
                    })
                    self.data_stats['processed_files'] += 1
        except Exception as e:
            logger.error(f"处理文件 {file_path} 时出错: {str(e)}")
            raise

    def _determine_data_type(self, ext):
        """确定数据类型"""
        if ext.lower() in ['.txt', '.pdf', '.docx']:
            return 'text'
        elif ext.lower() in ['.csv', '.xlsx', '.json']:
            return 'tabular'
        elif ext.lower() in ['.jpg', '.png']:
            return 'images'
        else:
            return 'metadata'

    # 以下是各种文件类型的处理器
    def _process_text(self, file_path):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    def _process_tabular(self, file_path):
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            return pd.read_excel(file_path)
        return None

    def _process_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _process_docx(self, file_path):
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])

    def _process_image(self, file_path):
        return Image.open(file_path)

    def _process_pdf(self, file_path):
        text = ""
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text

    def _process_zip(self, file_path):
        """处理ZIP文件并提取内容"""
        extracted_data = []
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                if not file_info.is_dir():
                    try:
                        with zip_ref.open(file_info) as file:
                            _, ext = os.path.splitext(file_info.filename)
                            if ext.lower() in self.supported_extensions:
                                content = None
                                if ext.lower() in ['.jpg', '.png']:
                                    content = Image.open(io.BytesIO(file.read()))
                                elif ext.lower() in ['.txt', '.pdf', '.docx']:
                                    content = file.read().decode('utf-8')
                                elif ext.lower() in ['.csv', '.xlsx']:
                                    content = pd.read_csv(io.BytesIO(file.read())) if ext == '.csv' else pd.read_excel(io.BytesIO(file.read()))
                                
                                if content is not None:
                                    extracted_data.append({
                                        'file_path': f"{file_path}/{file_info.filename}",
                                        'extension': ext.lower(),
                                        'content': content
                                    })
                    except Exception as e:
                        logger.error(f"处理ZIP内文件 {file_info.filename} 时出错: {str(e)}")
        return extracted_data

    def _clean_data(self):
        """清洗所有收集到的数据"""
        logger.info("开始数据清洗...")
        
        # 清洗文本数据
        self._clean_text_data()
        
        # 清洗表格数据
        self._clean_tabular_data()
        
        # 处理图像数据
        self._process_image_data()
        
        logger.info("数据清洗完成")

    def _clean_text_data(self):
        """清洗文本数据"""
        for item in tqdm(self.data_pipeline['text'], desc="清洗文本数据"):
            try:
                text = item['raw_data']
                # 清洗步骤
                cleaned = text.lower()  # 统一小写
                cleaned = ' '.join(cleaned.split())  # 去除多余空格
                cleaned = ''.join(c for c in cleaned if c.isalnum() or c.isspace())  # 保留字母数字和空格
                
                item['cleaned_data'] = cleaned
                item['status'] = 'cleaned'
            except Exception as e:
                logger.error(f"清洗文本数据失败 {item['file_path']}: {str(e)}")
                item['status'] = 'failed'

    def _clean_tabular_data(self):
        """清洗表格数据"""
        for item in tqdm(self.data_pipeline['tabular'], desc="清洗表格数据"):
            try:
                df = item['raw_data']
                # 清洗步骤
                df = df.dropna(thresh=len(df.columns)//2)  # 删除缺失值超过一半的行
                df = df.drop_duplicates()
                
                # 处理异常值
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                for col in numeric_cols:
                    q1 = df[col].quantile(0.25)
                    q3 = df[col].quantile(0.75)
                    iqr = q3 - q1
                    df[col] = np.where((df[col] < (q1 - 1.5*iqr)) | (df[col] > (q3 + 1.5*iqr)),
                                   df[col].median(), df[col])
                
                item['cleaned_data'] = df
                item['status'] = 'cleaned'
            except Exception as e:
                logger.error(f"清洗表格数据失败 {item['file_path']}: {str(e)}")
                item['status'] = 'failed'

    def _process_image_data(self):
        """处理图像数据"""
        for item in tqdm(self.data_pipeline['images'], desc="处理图像数据"):
            try:
                img = item['raw_data']
                # 标准化处理
                img = img.convert('RGB')  # 统一为RGB格式
                img = img.resize((256, 256))  # 统一尺寸
                
                item['cleaned_data'] = img
                item['status'] = 'cleaned'
            except Exception as e:
                logger.error(f"处理图像数据失败 {item['file_path']}: {str(e)}")
                item['status'] = 'failed'

    def _prepare_for_training(self):
        """准备训练数据格式"""
        logger.info("准备训练数据...")
        
        training_data = {
            'text_data': [],
            'tabular_data': [],
            'image_data': []
        }
        
        # 准备文本数据
        for item in self.data_pipeline['text']:
            if item['status'] == 'cleaned':
                training_data['text_data'].append(item['cleaned_data'])
        
        # 准备表格数据
        for item in self.data_pipeline['tabular']:
            if item['status'] == 'cleaned':
                training_data['tabular_data'].append(item['cleaned_data'])
        
        # 准备图像数据
        for item in self.data_pipeline['images']:
            if item['status'] == 'cleaned':
                training_data['image_data'].append(item['cleaned_data'])
        
        # 合并所有表格数据
        if training_data['tabular_data']:
            try:
                training_data['combined_tabular'] = pd.concat(training_data['tabular_data'], ignore_index=True)
            except Exception as e:
                logger.error(f"合并表格数据失败: {str(e)}")
                training_data['combined_tabular'] = None
        
        logger.info(f"准备完成: {len(training_data['text_data'])} 文本样本, "
                   f"{len(training_data['tabular_data'])} 表格数据集, "
                   f"{len(training_data['image_data'])} 图像样本")
        
        return training_data

# 使用示例
if __name__ == "__main__":
    # 初始化自动化数据投喂系统
    feeder = AutoDataFeeder()
    
    # 运行完整管道
    training_data = feeder.run_pipeline()
    
    # 这里可以添加代码将training_data投喂给模型
    # 例如:
    # model.train(text_data=training_data['text_data'],
    #             tabular_data=training_data['combined_tabular'],
    #             image_data=training_data['image_data'])
    
    print("数据已准备好，可以开始训练模型!")