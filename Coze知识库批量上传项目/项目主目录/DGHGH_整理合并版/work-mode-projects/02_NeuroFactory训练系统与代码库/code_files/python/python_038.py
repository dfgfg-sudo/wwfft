#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 Neuro Factory Pro 完整功能测试脚本
✅ 测试所有核心模块的集成功能
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
import json
import pandas as pd
from PIL import Image
import numpy as np

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.quantum_feeder import QuantumFeeder
from core.data_processor import DataProcessor
from core.model_trainer import ModelTrainer
from core.security import QuantumSecurity

class TestNeuroFactoryPro(unittest.TestCase):
    """Neuro Factory Pro 集成测试"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时测试数据
        self.test_dir = tempfile.mkdtemp(prefix="neuro_test_")
        print(f"测试目录: {self.test_dir}")
        
        # 创建测试文件
        self._create_test_files()
        
        # 初始化组件
        self.feeder = QuantumFeeder()
        self.processor = DataProcessor()
        self.trainer = ModelTrainer("microsoft/DialoGPT-small")
        self.security = QuantumSecurity()
    
    def _create_test_files(self):
        """创建测试文件"""
        # 1. 文本文件
        text_file = os.path.join(self.test_dir, "test.txt")
        with open(text_file, "w", encoding="utf-8") as f:
            f.write("这是测试文本文件。\n包含多行内容。\n用于测试量子数据吞噬引擎。")
        
        # 2. JSON文件
        json_file = os.path.join(self.test_dir, "test.json")
        data = {
            "name": "测试数据",
            "values": [1, 2, 3, 4, 5],
            "nested": {"key": "value"}
        }
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 3. CSV文件
        csv_file = os.path.join(self.test_dir, "test.csv")
        df = pd.DataFrame({
            "id": [1, 2, 3, 4, 5],
            "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
            "score": [85, 92, 78, 88, 95]
        })
        df.to_csv(csv_file, index=False)
        
        # 4. 图像文件
        img_file = os.path.join(self.test_dir, "test.png")
        img = Image.new('RGB', (100, 100), color='red')
        img.save(img_file)
        
        # 5. Python文件
        py_file = os.path.join(self.test_dir, "test.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("""
def test_function():
    '''测试函数'''
    return "Hello, Neuro Factory Pro!"

class TestClass:
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value

if __name__ == "__main__":
    print(test_function())
""")
        
        print(f"创建测试文件完成: {len(os.listdir(self.test_dir))} 个文件")
    
    def test_01_quantum_feeder(self):
        """测试量子数据吞噬引擎"""
        print("\n🔍 测试量子数据吞噬引擎...")
        
        # 吞噬数据
        data = list(self.feeder.devour([self.test_dir]))
        
        self.assertGreater(len(data), 0, "未读取到任何数据")
        print(f"读取到 {len(data)} 个数据项")
        
        # 检查数据类型
        types = [item['type'] for item in data]
        expected_types = ['text', 'json', 'csv', 'image', 'python']
        
        for expected in expected_types:
            self.assertIn(expected, types, f"缺少 {expected} 类型数据")
        
        print("✅ 量子数据吞噬测试通过")
    
    def test_02_data_processor(self):
        """测试数据处理"""
        print("\n🔍 测试数据处理...")
        
        # 读取数据
        data = list(self.feeder.devour([self.test_dir]))
        
        # 处理数据
        processed = self.processor.process_batch(data)
        
        self.assertIsNotNone(processed, "数据处理失败")
        self.assertTrue(hasattr(processed, '__len__'), "处理结果无效")
        
        print(f"处理了 {len(processed)} 个数据项")
        print("✅ 数据处理测试通过")
    
    def test_03_model_trainer(self):
        """测试模型训练"""
        print("\n🔍 测试模型训练...")
        
        # 读取数据
        data = list(self.feeder.devour([self.test_dir]))
        
        # 准备训练数据
        dataset = self.trainer.prepare_data(data)
        
        self.assertIsNotNone(dataset, "数据准备失败")
        print(f"准备训练数据: {len(dataset)} 条")
        
        # 测试模型初始化
        self.trainer.initialize_model()
        self.assertIsNotNone(self.trainer.model, "模型初始化失败")
        self.assertIsNotNone(self.trainer.tokenizer, "分词器初始化失败")
        
        print("✅ 模型训练基础测试通过")
    
    def test_04_security_encryption(self):
        """测试安全加密"""
        print("\n🔍 测试安全加密...")
        
        # 生成密钥
        key = self.security.generate_key()
        key_info = self.security.get_key_info()
        
        self.assertIsNotNone(key, "密钥生成失败")
        self.assertGreater(len(key_info['key_ids']), 0, "未生成密钥ID")
        
        # 测试数据加密
        test_data = {
            "secret": "这是机密数据",
            "timestamp": "2024-01-01T00:00:00",
            "value": 42
        }
        
        key_id = key_info['key_ids'][0]
        encrypted = self.security.encrypt_data(test_data, key_id)
        
        self.assertIn('encrypted_data', encrypted, "加密数据格式错误")
        self.assertIn('key_id', encrypted, "加密数据缺少密钥ID")
        
        # 测试数据解密
        decrypted = self.security.decrypt_data(encrypted)
        
        self.assertEqual(decrypted['secret'], test_data['secret'], "解密数据不匹配")
        self.assertEqual(decrypted['value'], test_data['value'], "解密数据值不匹配")
        
        print("✅ 安全加密测试通过")
    
    def test_05_integration_pipeline(self):
        """测试完整集成管道"""
        print("\n🔍 测试完整集成管道...")
        
        # 1. 数据吞噬
        raw_data = list(self.feeder.devour([self.test_dir]))
        self.assertGreater(len(raw_data), 0, "数据吞噬失败")
        
        # 2. 数据处理
        processed_data = self.processor.process_batch(raw_data)
        self.assertIsNotNone(processed_data, "数据处理失败")
        
        # 3. 数据加密
        key = self.security.generate_key()
        key_id = list(self.security.get_key_info()['key_ids'])[0]
        
        # 加密部分数据
        sample_data = raw_data[0] if raw_data else {"test": "data"}
        encrypted = self.security.encrypt_data(sample_data, key_id)
        self.assertIn('encrypted_data', encrypted, "加密失败")
        
        # 4. 模型初始化
        self.trainer.initialize_model()
        self.assertIsNotNone(self.trainer.model, "模型初始化失败")
        
        print("✅ 完整集成管道测试通过")
    
    def test_06_error_handling(self):
        """测试错误处理"""
        print("\n🔍 测试错误处理...")
        
        # 测试无效路径
        invalid_path = "/invalid/path/that/does/not/exist"
        data = list(self.feeder.devour([invalid_path]))
        self.assertEqual(len(data), 0, "应该处理无效路径")
        
        # 测试无效文件
        invalid_file = os.path.join(self.test_dir, "invalid.bin")
        with open(invalid_file, "wb") as f:
            f.write(b"\x00\x01\x02\x03\x04\x05")
        
        data = list(self.feeder.devour([invalid_file]))
        # 应该至少返回一个通用格式的结果
        self.assertGreater(len(data), 0, "应该处理无效文件")
        
        print("✅ 错误处理测试通过")
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            print(f"清理测试目录: {self.test_dir}")

def run_all_tests():
    """运行所有测试"""
    print("""
    ╔══════════════════════════════════════════════╗
    ║  🧪 Neuro Factory Pro 完整功能测试套件        ║
    ╚══════════════════════════════════════════════╝
    """)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestNeuroFactoryPro)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出总结
    print(f"""
    📊 测试总结:
        运行测试: {result.testsRun}
        失败: {len(result.failures)}
        错误: {len(result.errors)}
        跳过: {len(result.skipped)}
    """)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)