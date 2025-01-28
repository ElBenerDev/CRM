from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import sys

from app.utils.db import get_db
from app.models.models import User

# Configuración de JWT
SECRET_KEY = "tu_clave_secreta_aqui"  # Cambia esto por una clave segura
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuración de password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def log_auth(message: str):
    """Función auxiliar para logging de autenticación"""
    print(f"[AUTH] {message}")
    sys.stdout.flush()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña coincide con el hash"""
    try:
        log_auth(f"Verificando contraseña...")
        result = pwd_context.verify(plain_password, hashed_password)
        log_auth(f"Resultado verificación: {'✅ Correcto' if result else '❌ Incorrecto'}")
        return result
    except Exception as e:
        log_auth(f"❌ Error verificando contraseña: {str(e)}")
        return False

def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT"""
    try:
        log_auth("🎟️ Generando token de acceso...")
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
            
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        log_auth("✅ Token generado correctamente")
        return encoded_jwt
    except Exception as e:
        log_auth(f"❌ Error generando token: {str(e)}")
        raise

def decode_token(token: str) -> dict:
    """Decodifica un token JWT"""
    try:
        log_auth("🔍 Decodificando token...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        log_auth("✅ Token decodificado correctamente")
        return payload
    except JWTError as e:
        log_auth(f"❌ Error decodificando token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

async def get_current_user(token: str = None, db: Session = Depends(get_db)) -> User:
    """Obtiene el usuario actual basado en el token JWT"""
    try:
        log_auth("👤 Obteniendo usuario actual...")
        
        if not token:
            log_auth("❌ No se proporcionó token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No autenticado"
            )
            
        if token.startswith("Bearer "):
            token = token.split(" ")[1]
            
        payload = decode_token(token)
        email: str = payload.get("sub")
        
        if email is None:
            log_auth("❌ Token no contiene email")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
            
        user = db.query(User).filter(User.email == email).first()
        if not user:
            log_auth("❌ Usuario no encontrado en DB")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado"
            )
            
        log_auth(f"✅ Usuario autenticado: {user.email}")
        return user
        
    except Exception as e:
        log_auth(f"❌ Error en autenticación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error de autenticación"
        )