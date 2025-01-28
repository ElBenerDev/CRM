from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Form
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import timedelta
import logging
import sys
import traceback

# Importaciones locales
from app.utils.db import get_db
from app.models.models import User
from app.schemas.schemas import UserCreate, UserResponse, Token
from app.core.templates import templates
from .utils import (
    authenticate_user, 
    create_access_token, 
    get_password_hash,
    verify_password,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Configuración del router
router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

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
        
        # Verificar contraseña
        logger.info("🔒 Verificando contraseña...")
        if not verify_password(password, user.password):
            logger.error("❌ Contraseña incorrecta")
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Email o contraseña incorrectos"}
            )
        
        logger.info("✅ Contraseña verificada correctamente")
        
        # Crear token y establecer cookie
        logger.info("🎟️ Generando token de acceso...")
        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=1800,
            path="/"
        )
        
        logger.info("✅ Token generado y cookie establecida")
        logger.info("✅ Login exitoso - Redirigiendo al dashboard")
        logger.info("="*50)
        return response
        
    except Exception as e:
        logger.error("\n❌ Error en el proceso de login:")
        logger.error(str(e))
        logger.error("📋 Traceback completo:")
        logger.error(traceback.format_exc())
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Error del servidor"}
        )
        
@router.get("/login")
async def login_page(request: Request):
    try:
        # Si hay un token activo, redirigir al dashboard
        if request.cookies.get("access_token"):
            logger.info("🔄 Usuario ya autenticado, redirigiendo al dashboard")
            return RedirectResponse(url="/", status_code=302)
        
        logger.info("📝 Mostrando página de login")
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request}
        )
    except Exception as e:
        logger.error(f"❌ Error en login_page: {str(e)}")
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Error del servidor"}
        )

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    logger.info("\n" + "="*50)
    logger.info("📝 INICIO DEL PROCESO DE REGISTRO")
    logger.info(f"📧 Email a registrar: {user.email}")
    
    try:
        # Verificar si el usuario ya existe
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user:
            logger.warning("⚠️ Intento de registro con email existente")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Crear nuevo usuario
        logger.info("🔒 Hasheando contraseña...")
        hashed_password = get_password_hash(user.password)
        
        logger.info("👤 Creando nuevo usuario...")
        db_user = User(
            email=user.email,
            password=hashed_password,
            name=user.name
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info("✅ Usuario registrado correctamente")
        logger.info("="*50)
        return db_user
    
    except HTTPException as he:
        logger.error(f"⚠️ Error de validación: {str(he.detail)}")
        raise he
    except Exception as e:
        logger.error("❌ Error en el proceso de registro:")
        logger.error(str(e))
        logger.error(traceback.format_exc())
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar usuario: {str(e)}"
        )

@router.get("/logout")
async def logout():
    logger.info("🚪 Proceso de logout iniciado")
    try:
        response = RedirectResponse(url="/auth/login", status_code=302)
        response.delete_cookie(
            key="access_token",
            path="/",
            secure=True,
            httponly=True
        )
        logger.info("✅ Logout exitoso")
        return response
    except Exception as e:
        logger.error(f"❌ Error en logout: {str(e)}")
        return RedirectResponse(url="/auth/login", status_code=302)