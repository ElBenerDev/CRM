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
        # Asegurarnos de que trabajamos con strings UTF-8
        if isinstance(plain_password, bytes):
            plain_password = plain_password.decode('utf-8')
        if isinstance(hashed_password, bytes):
            hashed_password = hashed_password.decode('utf-8')
            
        # Generar el hash con la misma sal
        salt = hashed_password[:29].encode('utf-8')  # Obtener la sal del hash existente
        calculated_hash = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
        
        print(f"Calculated hash: {calculated_hash}")
        print(f"Stored hash: {hashed_password.encode('utf-8')}")
        
        return calculated_hash == hashed_password.encode('utf-8')
    except Exception as e:
        print(f"Error verificando contraseña: {str(e)}")
        print(f"Tipo de error: {type(e)}")
        return False

def get_password_hash(password: str) -> str:
    # Usar una sal específica para asegurar consistencia
    salt = bcrypt.gensalt(rounds=12, prefix=b'2b')
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')