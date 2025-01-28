from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.utils.db import get_db
from app.models.models import User
from app.schemas.schemas import UserCreate, UserResponse, Token
from .utils import (
    authenticate_user, 
    create_access_token, 
    get_password_hash,
    verify_password,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from datetime import timedelta
from app.core.templates import templates  # Cambia esta línea
from fastapi import Form
from app.utils.logging_config import logger


import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
import sys

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
logger = logging.getLogger(__name__)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # Esto asegura que los logs vayan a stdout
    ]
)
app = FastAPI(title=settings.APP_NAME)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response Status: {response.status_code}")
    return response


@router.post("/token")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    logger.info("\n" + "="*50)
    logger.info("🔐 INICIO DEL PROCESO DE LOGIN")
    logger.info(f"📧 Email recibido: {username}")
    
    try:
        # Verificar conexión a DB
        logger.info("📊 Verificando conexión a base de datos...")
        db.execute(text("SELECT 1"))
        logger.info("✅ Conexión a DB verificada")
        
        # Buscar usuario
        logger.info("🔍 Buscando usuario...")
        user = db.query(User).filter(User.email == username).first()
        
        if not user:
            logger.error("❌ Usuario no encontrado")
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Email o contraseña incorrectos"}
            )
        
        logger.info(f"✅ Usuario encontrado: {user.email}")
        logger.info(f"👤 Nombre: {user.name}")
        logger.info(f"📅 Creado: {user.created_at}")
        
        # Verificar contraseña
        logger.info("🔒 Verificando contraseña...")
        if not verify_password(password, user.password):
            logger.error("❌ Contraseña incorrecta")
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Email o contraseña incorrectos"}
            )
        
        logger.info("✅ Contraseña verificada correctamente")
        
        # Crear y establecer token
        logger.info("🎟️ Generando token...")
        access_token = create_access_token(data={"sub": user.email})
        
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=1800
        )
        
        logger.info("✅ Token generado y cookie establecida")
        logger.info("✅ Login exitoso - Redirigiendo al dashboard")
        logger.info("="*50)
        return response
        
    except Exception as e:
        logger.error("\n❌ Error en el proceso de login:")
        logger.error(str(e))
        logger.error("Traceback:", exc_info=True)
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Error del servidor"}
        )
        
@router.get("/login")
async def login_page(request: Request):
    # Si hay un token activo, redirigir al dashboard
    if request.cookies.get("access_token"):
        return RedirectResponse(url="/", status_code=302)
    
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request}
    )

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            password=hashed_password,
            name=user.name
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar usuario: {str(e)}"
        )

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie(
        key="access_token",
        path="/"
    )
    return response