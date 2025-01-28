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
    create_access_token, 
    get_password_hash,
    verify_password,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    log_auth  # Nueva función de logging
)

# Configuración del router
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/token")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
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
        log_auth("🔍 Buscando usuario...")
        user = db.query(User).filter(User.email == username).first()
        
        if not user:
            log_auth("❌ Usuario no encontrado")
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Email o contraseña incorrectos"},
                status_code=401
            )
        
        log_auth(f"✅ Usuario encontrado: {user.email}")
        log_auth(f"👤 Nombre: {user.name}")
        
        # Verificar contraseña
        log_auth("🔒 Verificando contraseña...")
        if not verify_password(password, user.password):
            log_auth("❌ Contraseña incorrecta")
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Email o contraseña incorrectos"},
                status_code=401
            )
        
        log_auth("✅ Contraseña verificada correctamente")
        
        # Crear token
        log_auth("🎟️ Generando token...")
        try:
            access_token = create_access_token(
                data={"sub": user.email},
                expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            log_auth("✅ Token generado")
        except Exception as e:
            log_auth(f"❌ Error generando token: {str(e)}")
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Error del servidor"},
                status_code=500
            )
        
        # Crear respuesta
        try:
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
            log_auth(f"❌ Error estableciendo cookie: {str(e)}")
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Error del servidor"},
                status_code=500
            )
        
    except Exception as e:
        log_auth("\n❌ ERROR EN LOGIN:")
        log_auth(str(e))
        log_auth(traceback.format_exc())
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Error del servidor"},
            status_code=500
        )

@router.get("/login")
async def login_page(request: Request):
    log_auth("📄 Accediendo a la página de login")
    if request.cookies.get("access_token"):
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.get("/logout")
async def logout():
    log_auth("🚪 Iniciando logout")
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie(
        key="access_token",
        path="/",
        secure=True,
        httponly=True
    )
    log_auth("✅ Logout completado")
    return response