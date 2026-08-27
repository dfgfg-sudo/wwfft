from cryptography.fernet import Fernet
import hashlib
import hmac

class QuantumSecurity:
    def __init__(self, config: NeuroConfig):
        self.cipher = Fernet(config.quantum_key)
        self.key = config.quantum_key

    def encrypt(self, data: bytes) -> bytes:
        return self.cipher.encrypt(data)

    def decrypt(self, ciphertext: bytes) -> bytes:
        return self.cipher.decrypt(ciphertext)

    def encrypt_file(self, path: Path):
        data = path.read_bytes()
        encrypted = self.encrypt(data)
        path.with_suffix(path.suffix + ".enc").write_bytes(encrypted)

    def decrypt_file(self, enc_path: Path):
        data = enc_path.read_bytes()
        decrypted = self.decrypt(data)
        orig_path = enc_path.with_suffix("")
        orig_path.write_bytes(decrypted)

    def sign(self, data: bytes) -> str:
        return hmac.new(self.key, data, hashlib.sha256).hexdigest()