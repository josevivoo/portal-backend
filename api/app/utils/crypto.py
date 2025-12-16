from cryptography.fernet import Fernet
import os
import base64

# LEER DEL ENTORNO
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

if not ENCRYPTION_KEY:
    raise ValueError("FATAL: ENCRYPTION_KEY no está configurada en las variables de entorno.")

try:
    cipher_suite = Fernet(ENCRYPTION_KEY.encode())
except Exception as e:
    raise ValueError(f"FATAL: ENCRYPTION_KEY inválida. Asegúrate de que es una clave Fernet válida (32 bytes base64). Error: {e}")

def encrypt_value(value: str) -> str:
    """Cifra un string y devuelve el hash en string"""
    if not value:
        return None
    return cipher_suite.encrypt(value.encode()).decode()

def decrypt_value(hashed_value: str) -> str:
    """Descifra un hash y devuelve el string original"""
    if not hashed_value:
        return None
    try:
        return cipher_suite.decrypt(hashed_value.encode()).decode()
    except Exception:
        # Es buena práctica manejar errores de descifrado (ej. clave incorrecta o datos corruptos)
        return None