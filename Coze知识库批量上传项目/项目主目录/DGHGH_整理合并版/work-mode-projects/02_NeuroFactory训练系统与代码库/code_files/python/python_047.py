# -*- coding: utf-8 -*-
"""
🔐 量子安全加密模块
✅ 提供军事级数据保护
"""

import os
import hashlib
import hmac
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import json
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class QuantumSecurity:
    """量子安全加密模块"""
    
    def __init__(self, key_size: int = 32):
        self.key_size = key_size
        self.encryption_keys = {}
        self.backend = default_backend()
        
        logger.info("量子安全模块初始化完成")
    
    def generate_key(self, password: Optional[str] = None) -> bytes:
        """生成加密密钥"""
        if password:
            # 使用密码生成密钥
            salt = os.urandom(16)
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=self.key_size,
                salt=salt,
                iterations=100000,
                backend=self.backend
            )
            key = kdf.derive(password.encode())
        else:
            # 生成随机密钥
            key = os.urandom(self.key_size)
        
        # 保存密钥
        key_id = hashlib.sha256(key).hexdigest()[:16]
        self.encryption_keys[key_id] = {
            'key': key,
            'salt': salt if password else None,
            'created': datetime.now().isoformat()
        }
        
        logger.info(f"生成密钥: {key_id}")
        return key
    
    def encrypt_data(self, data: Any, key_id: str) -> Dict[str, Any]:
        """加密数据"""
        if key_id not in self.encryption_keys:
            raise ValueError(f"密钥不存在: {key_id}")
        
        key_info = self.encryption_keys[key_id]
        key = key_info['key']
        
        # 序列化数据
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, ensure_ascii=False)
        else:
            data_str = str(data)
        
        data_bytes = data_str.encode('utf-8')
        
        # 生成初始化向量
        iv = os.urandom(16)
        
        # 创建加密器
        cipher = Cipher(
            algorithms.AES(key),
            modes.CFB(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        
        # 加密数据
        encrypted_data = encryptor.update(data_bytes) + encryptor.finalize()
        
        # 计算HMAC
        hmac_obj = hmac.new(key, encrypted_data, hashlib.sha256)
        hmac_digest = hmac_obj.digest()
        
        result = {
            'encrypted_data': base64.b64encode(encrypted_data).decode('ascii'),
            'iv': base64.b64encode(iv).decode('ascii'),
            'hmac': base64.b64encode(hmac_digest).decode('ascii'),
            'key_id': key_id,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"数据加密完成: {len(data_bytes)} 字节")
        return result
    
    def decrypt_data(self, encrypted_package: Dict[str, Any]) -> Any:
        """解密数据"""
        key_id = encrypted_package.get('key_id')
        if key_id not in self.encryption_keys:
            raise ValueError(f"密钥不存在: {key_id}")
        
        key_info = self.encryption_keys[key_id]
        key = key_info['key']
        
        # 解码数据
        encrypted_data = base64.b64decode(encrypted_package['encrypted_data'])
        iv = base64.b64decode(encrypted_package['iv'])
        hmac_received = base64.b64decode(encrypted_package['hmac'])
        
        # 验证HMAC
        hmac_obj = hmac.new(key, encrypted_data, hashlib.sha256)
        hmac_calculated = hmac_obj.digest()
        
        if not hmac.compare_digest(hmac_received, hmac_calculated):
            raise ValueError("HMAC验证失败，数据可能被篡改")
        
        # 创建解密器
        cipher = Cipher(
            algorithms.AES(key),
            modes.CFB(iv),
            backend=self.backend
        )
        decryptor = cipher.decryptor()
        
        # 解密数据
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # 反序列化数据
        try:
            result = json.loads(decrypted_data.decode('utf-8'))
        except json.JSONDecodeError:
            result = decrypted_data.decode('utf-8')
        
        logger.info("数据解密成功")
        return result
    
    def encrypt_file(self, file_path: str, key_id: str, output_path: Optional[str] = None):
        """加密文件"""
        with open(file_path, 'rb') as f:
            data = f.read()
        
        # 使用Fernet加密（更简单的方法）
        key = base64.urlsafe_b64encode(self.encryption_keys[key_id]['key'][:32])
        fernet = Fernet(key)
        
        encrypted_data = fernet.encrypt(data)
        
        if output_path is None:
            output_path = file_path + '.encrypted'
        
        with open(output_path, 'wb') as f:
            f.write(encrypted_data)
        
        logger.info(f"文件加密完成: {file_path} -> {output_path}")
        return output_path
    
    def decrypt_file(self, encrypted_file: str, key_id: str, output_path: Optional[str] = None):
        """解密文件"""
        with open(encrypted_file, 'rb') as f:
            encrypted_data = f.read()
        
        key = base64.urlsafe_b64encode(self.encryption_keys[key_id]['key'][:32])
        fernet = Fernet(key)
        
        decrypted_data = fernet.decrypt(encrypted_data)
        
        if output_path is None:
            if encrypted_file.endswith('.encrypted'):
                output_path = encrypted_file[:-10]
            else:
                output_path = encrypted_file + '.decrypted'
        
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
        
        logger.info(f"文件解密完成: {encrypted_file} -> {output_path}")
        return output_path
    
    def get_key_info(self) -> Dict[str, Any]:
        """获取密钥信息"""
        info = {
            'total_keys': len(self.encryption_keys),
            'key_ids': list(self.encryption_keys.keys()),
            'key_size': self.key_size
        }
        return info