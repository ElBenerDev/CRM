from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.models.models import User
import sys
import traceback

# Configuración de JWT
SECRET_KEY = "8f96d3a4e5b7c9d1f2g3h4j5k6l7m8n9p0q1r2s3t4u5v6w7x8y9z"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuración de password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def log_auth(message: str):
    """Función auxiliar para logging de autenticación"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [AUTH] {message}")
    sys.stdout.flush()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Error verificando contraseña: {str(e)}")
        return False

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = None, db: Session = Depends(get_db)) -> User:
    """Obtiene el usuario actual basado en el token JWT"""
    try:
        log_auth("👤 Verificando usuario actual...")
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudieron validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )

        if not token:
            log_auth("❌ No se proporcionó token")
            raise credentials_exception

        # Eliminar 'Bearer ' si está presente
        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        try:
            # Decodificar token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                log_auth("❌ Token no contiene email")
                raise credentials_exception
        except JWTError as e:
            log_auth(f"❌ Error decodificando token: {str(e)}")
            raise credentials_exception

        # Buscar usuario en la base de datos
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            log_auth("❌ Usuario no encontrado en base de datos")
            raise credentials_exception

        log_auth(f"✅ Usuario autenticado: {user.email}")
        return user

    except Exception as e:
        log_auth(f"❌ Error en autenticación: {str(e)}")
        log_auth(traceback.format_exc())
        raise credentials_exception