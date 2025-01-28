from passlib.hash import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.models.models import User
from app.utils.db import get_db

# Configuración de Seguridad
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Configuración de JWT
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # Cambiar en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Error verificando contraseña: {str(e)}")
        return False

def get_password_hash(password: str) -> str:
    try:
        return bcrypt.hash(password)
    except Exception as e:
        print(f"Error hasheando contraseña: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error al procesar la contraseña"
        )

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        print(f"Error creando token: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error al crear el token de acceso"
        )

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    try:
        print(f"Buscando usuario con email: {email}")
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print("Usuario no encontrado")
            return None
            
        if not verify_password(password, user.password):
            print("Contraseña incorrecta")
            return None
            
        print("Usuario autenticado correctamente")
        return user
        
    except Exception as e:
        print(f"Error en authenticate_user: {str(e)}")
        return None

async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError as e:
        print(f"Error decodificando token: {str(e)}")
        raise credentials_exception
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        raise credentials_exception

    try:
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise credentials_exception
        return user
    except Exception as e:
        print(f"Error consultando usuario: {str(e)}")
        raise credentials_exception