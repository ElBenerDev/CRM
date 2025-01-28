from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
import sys
import traceback

# Configuración de JWT
SECRET_KEY = "M9FE2yP#kL8$vX@5nJ3mQ7wR*tZ6hN4cB2dV9sG"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuración de password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def log_auth(message: str):
    """Función auxiliar para logging de autenticación"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [AUTH] {message}")
    sys.stdout.flush()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña coincide con el hash"""
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        return result
    except Exception as e:
        log_auth(f"❌ Error verificando contraseña: {str(e)}")
        log_auth(traceback.format_exc())
        return False

def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT"""
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        log_auth(f"❌ Error creando token: {str(e)}")
        log_auth(traceback.format_exc())
        raise