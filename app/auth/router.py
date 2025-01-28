from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Form
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import timedelta, datetime
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
    print("\n" + "="*50)
    print(f"[LOGIN] Intento de inicio de sesión")
    print(f"[LOGIN] Email: {username}")
    print(f"[LOGIN] Timestamp: {datetime.now()}")
    print("-"*50)

    try:
        # 1. Verificar conexión DB
        print("[LOGIN] 1. Verificando conexión a DB...")
        try:
            db.execute(text("SELECT 1"))
            print("[LOGIN] ✓ Conexión a DB verificada")
        except Exception as e:
            print(f"[LOGIN] ✗ Error de conexión: {str(e)}")
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Error de conexión a la base de datos"},
                status_code=500
            )

        # 2. Buscar usuario
        print("[LOGIN] 2. Buscando usuario...")
        user = db.query(User).filter(User.email == username).first()
        
        if not user:
            print(f"[LOGIN] ✗ Usuario no encontrado: {username}")
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Email o contraseña incorrectos"},
                status_code=401
            )
        
        print(f"[LOGIN] ✓ Usuario encontrado: {user.email}")

        # 3. Verificar contraseña
        print("[LOGIN] 3. Verificando contraseña...")
        if not verify_password(password, user.password):
            print("[LOGIN] ✗ Contraseña incorrecta")
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Email o contraseña incorrectos"},
                status_code=401
            )
        
        print("[LOGIN] ✓ Contraseña verificada")

        # 4. Generar token
        print("[LOGIN] 4. Generando token...")
        try:
            access_token = create_access_token(
                data={"sub": user.email},
                expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            print("[LOGIN] ✓ Token generado")
        except Exception as e:
            print(f"[LOGIN] ✗ Error generando token: {str(e)}")
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Error generando credenciales"},
                status_code=500
            )

        # 5. Crear respuesta
        print("[LOGIN] 5. Preparando respuesta...")
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
        
        print("[LOGIN] ✓ Cookie establecida")
        print("[LOGIN] ✓ Login exitoso")
        print("="*50)
        
        return response

    except Exception as e:
        print("\n[LOGIN] ¡ERROR CRÍTICO!")
        print(f"[LOGIN] Error: {str(e)}")
        print("[LOGIN] Traceback:")
        traceback.print_exc()
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