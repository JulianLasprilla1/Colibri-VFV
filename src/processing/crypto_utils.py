# src/processing/crypto_utils.py
from cryptography.fernet import Fernet
from config import ENCRYPTION_KEY # Asegúrate de definir ENCRYPTION_KEY en config.py

def encrypt_password(password: str) -> str:
    f = Fernet(ENCRYPTION_KEY)
    return f.encrypt(password.encode()).decode()

def decrypt_password(token: str) -> str:
    f = Fernet(ENCRYPTION_KEY)
    return f.decrypt(token.encode()).decode()
