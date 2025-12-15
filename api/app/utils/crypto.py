from cryptography.fernet import Fernet
import os
import base64

# En producción, esto debe ser una variable de entorno persistente
# Generamos una key fija temporalmente para que no cambie al reiniciar el contenedor
SECRET_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())

cipher_suite = Fernet(SECRET_KEY.encode() if isinstance(SECRET_KEY, str) else SECRET_KEY)

def encrypt_value(value: str) -> str:
    """Cifra un string y devuelve el hash en string"""
    if not value:
        return None
    return cipher_suite.encrypt(value.encode()).decode()

def decrypt_value(hashed_value: str) -> str:
    """Descifra un hash y devuelve el string original"""
    if not hashed_value:
        return None
    return cipher_suite.decrypt(hashed_value.encode()).decode()