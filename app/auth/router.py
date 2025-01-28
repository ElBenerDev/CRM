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

def log_debug(message: str):
    """Función para asegurar que los logs se muestren en la consola"""
    print(f"\n[DEBUG] {message}")
    sys.stdout.flush()

@router.post("/token")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    from .utils import log_auth  # Importar la función de logging
    
    log_auth("\n" + "="*50)
    log_auth("🔐 INICIO DEL PROCESO DE LOGIN")
    log_auth(f"📧 Email recibido: {username}")
    
    try:
        # Verificar conexión a DB
        log_auth("📊 Verificando conexión a base de datos...")
        try:
            db.execute(text("SELECT 1"))
            log_auth("✅ Conexión a DB verificada")
        except Exception as e:
            log_auth(f"❌ Error de conexión a DB: {str(e)}")
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Error de conexión"},
                status_code=500
            )

        # Buscar usuario
        log_auth("🔍 Buscando usuario en la base de datos...")
        user = db.query(User).filter(User.email == username).first()
        
        if not user:
            log_auth("❌ Usuario no encontrado")
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Email o contraseña incorrectos"},
                status_code=401
            )
        
        log_auth(f"✅ Usuario encontrado: {user.email}")
        
        # Verificar contraseña
        if not verify_password(password, user.password):
            log_auth("❌ Contraseña incorrecta")
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Email o contraseña incorrectos"},
                status_code=401
            )
        
        log_auth("✅ Autenticación exitosa")
        
        # Crear token
        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # Crear respuesta
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
        
        log_auth("✅ Cookie establecida correctamente")
        log_auth("✅ Login exitoso - Redirigiendo al dashboard")
        log_auth("="*50)
        return response
        
    except Exception as e:
        log_auth("\n❌ ERROR EN LOGIN:")
        log_auth(str(e))
        import traceback
        log_auth(traceback.format_exc())
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Error del servidor"},
            status_code=500
        )

@router.get("/login")
async def login_page(request: Request):
    log_debug("📄 Accediendo a la página de login")
    try:
        if request.cookies.get("access_token"):
            log_debug("🔄 Usuario ya autenticado, redirigiendo al dashboard")
            return RedirectResponse(url="/", status_code=302)
        log_debug("📝 Mostrando formulario de login")
        return templates.TemplateResponse("auth/login.html", {"request": request})
    except Exception as e:
        log_debug(f"❌ Error en página de login: {str(e)}")
        log_debug(traceback.format_exc())
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Error cargando la página"},
            status_code=500
        )

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    log_debug("\n" + "="*50)
    log_debug("📝 INICIO DEL PROCESO DE REGISTRO")
    log_debug(f"📧 Email a registrar: {user.email}")
    
    try:
        # Verificar si el usuario existe
        log_debug("🔍 Verificando si el email ya existe...")
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user:
            log_debug("❌ El email ya está registrado")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Crear nuevo usuario
        log_debug("🔒 Hasheando contraseña...")
        hashed_password = get_password_hash(user.password)
        
        log_debug("👤 Creando nuevo usuario...")
        db_user = User(
            email=user.email,
            password=hashed_password,
            name=user.name
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        log_debug("✅ Usuario registrado correctamente")
        log_debug("="*50)
        return db_user
        
    except HTTPException as he:
        log_debug(f"❌ Error de validación: {str(he.detail)}")
        raise he
    except Exception as e:
        log_debug("❌ Error en el proceso de registro:")
        log_debug(str(e))
        log_debug(traceback.format_exc())
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar usuario: {str(e)}"
        )

@router.get("/logout")
async def logout():
    log_debug("🚪 Iniciando proceso de logout")
    try:
        response = RedirectResponse(url="/auth/login", status_code=302)
        response.delete_cookie(
            key="access_token",
            path="/",
            secure=True,
            httponly=True
        )
        log_debug("✅ Logout exitoso")
        return response
    except Exception as e:
        log_debug(f"❌ Error en logout: {str(e)}")
        log_debug(traceback.format_exc())
        return RedirectResponse(url="/auth/login", status_code=302)