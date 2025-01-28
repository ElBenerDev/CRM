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
    # Logs iniciales
    print("\n" + "="*50)
    print(f"🔄 INICIO DE LOGIN - {datetime.now()}")
    print(f"📧 Usuario intentando login: {username}")
    
    try:
        # 1. Verificar conexión a DB
        print("1️⃣ Verificando conexión a base de datos...")
        try:
            db.execute(text("SELECT 1"))
            print("✅ Conexión a DB verificada")
        except Exception as e:
            print(f"❌ Error de conexión a DB: {str(e)}")
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Error de conexión a la base de datos"},
                status_code=500
            )

        # 2. Buscar usuario
        print("2️⃣ Buscando usuario en la base de datos...")
        user = db.query(User).filter(User.email == username).first()
        
        if not user:
            print(f"❌ Usuario no encontrado: {username}")
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Email o contraseña incorrectos"},
                status_code=401
            )
        
        print(f"✅ Usuario encontrado: {user.email}")
        
        # 3. Verificar contraseña
        print("3️⃣ Verificando contraseña...")
        valid_password = verify_password(password, user.password)
        print(f"Resultado verificación: {'✅ Correcta' if valid_password else '❌ Incorrecta'}")
        
        if not valid_password:
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Email o contraseña incorrectos"},
                status_code=401
            )

        # 4. Generar token
        print("4️⃣ Generando token...")
        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        print("✅ Token generado correctamente")

        # 5. Crear respuesta
        print("5️⃣ Preparando respuesta...")
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
        
        print("✅ Cookie establecida correctamente")
        print("✅ Login exitoso - Redirigiendo al dashboard")
        print("="*50)
        
        return response
        
    except Exception as e:
        print("\n❌ ERROR EN PROCESO DE LOGIN:")
        print(f"Error: {str(e)}")
        print("Traceback completo:")
        traceback.print_exc()
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Error interno del servidor"},
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