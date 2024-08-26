import pytest
from cryptography.fernet import Fernet

from common.settings import settings
from services.Encryption import EncryptionService, encryption_service


@pytest.mark.parametrize(
    "secret_key",
    (
        settings.SECRET_KEY,
        'a1b2_c3-d4?e5(f6)g7^h8*',
        'abc',
        '&*^_±!@#$%^&*()_+ё',
        'Русские сисволы с пробелами'
    )
)
def test_encrypt_decrypt(secret_key):
    # encryption_service = EncryptionService(secret_key)
    original_data = "MySecretData"
    encrypted_data = encryption_service.encrypt(original_data)
    decrypted_data = encryption_service.decrypt(encrypted_data)
    assert original_data == decrypted_data

