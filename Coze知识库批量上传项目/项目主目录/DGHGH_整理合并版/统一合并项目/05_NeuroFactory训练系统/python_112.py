from cryptography.fernet import Fernet
import base64

class SecurityManager:
    def __init__(self, key=None):
        self.key = key or Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def encrypt_data(self, data: bytes) -> bytes:
        return self.cipher.encrypt(data)

    def decrypt_data(self, data: bytes) -> bytes:
        return self.cipher.decrypt(data)

    def encrypt_model_weights(self, model_path, out_path):
        with open(model_path, 'rb') as f:
            enc = self.encrypt_data(f.read())
        with open(out_path, 'wb') as f:
            f.write(enc)