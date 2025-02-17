from datetime import datetime, timedelta
from typing import Any, Union
import bcrypt
from jose import jwt
from app.core.config import settings

def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm="HS256"
    )
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        # Convertir las contraseñas a bytes
        plain_password_bytes = plain_password.encode('utf-8')
        hashed_password_bytes = hashed_password.encode('utf-8')
        
        # Imprimir información de depuración
        print(f"Plain password: {plain_password}")
        print(f"Hashed password from DB: {hashed_password}")
        print(f"Plain password bytes: {plain_password_bytes}")
        print(f"Hashed password bytes: {hashed_password_bytes}")
        
        result = bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)
        print(f"Password verification result: {result}")
        return result
    except Exception as e:
        print(f"Error verificando contraseña: {str(e)}")
        print(f"Tipo de error: {type(e)}")
        return False

def get_password_hash(password: str) -> str:
    # Generar salt y hash
    salt = bcrypt.gensalt(12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')