from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from base64 import b64encode, b64decode
import hashlib

from common.settings import settings


class EncryptionService:
    def __init__(self, key: str):
        # Генерация 256-битного ключа из полученной строки
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, data: str) -> str:
        # Инициализация AES в режиме CBC с случайным вектором инициализации (IV)
        iv = algorithms.AES(self.key).block_size.to_bytes(16, byteorder='big')
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # Подготовка данных (выравнивание/паддинг)
        padder = padding.PKCS7(algorithms.AES(self.key).block_size).padder()
        padded_data = padder.update(data.encode()) + padder.finalize()

        # Шифрование
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        # Сочетание iv и шифрованных данных, чтобы можно было расшифровать
        return b64encode(iv + encrypted_data).decode()

    def decrypt(self, encrypted_data: str) -> str:
        # Декодирование base64 и разделение iv и шифрованных данных
        encrypted_data = b64decode(encrypted_data)
        iv = encrypted_data[:16]
        encrypted_data = encrypted_data[16:]

        # Инициализация AES в режиме CBC с использованием полученного iv
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        # Дешифрование
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

        # Удаление паддинга
        unpadder = padding.PKCS7(algorithms.AES(self.key).block_size).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()

        return data.decode()


encryption_service = EncryptionService(key=settings.SECRET_KEY)
