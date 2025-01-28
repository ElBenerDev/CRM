from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import text
import sys
import traceback
import os

from app.utils.db import get_db
from app.models.models import User
from .utils import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/auth", tags=["auth"])
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "app", "templates"))

def log_debug(message: str):
    print(f"[DEBUG][{datetime.now()}] {message}", file=sys.stdout)
    sys.stdout.flush()

@router.get("/login")
async def login_page(request: Request):
    print(f"Template directory: {os.path.join(BASE_DIR, 'app', 'templates')}")
    print(f"Current directory: {os.getcwd()}")
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.post("/token")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    log_debug("\n" + "="*50)
    log_debug("INICIO DE PROCESO DE LOGIN")
    log_debug(f"Usuario: {username}")

    try:
        # 1. Verificar conexión a DB
        log_debug("1. Verificando conexión a DB...")
        try:
            db.execute(text("SELECT 1"))
            log_debug("✓ Conexión a DB OK")
        except Exception as e:
            log_debug(f"✗ Error de conexión: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"error": "Error de conexión a la base de datos"}
            )

        # 2. Buscar usuario
        log_debug("2. Buscando usuario...")
        user = db.query(User).filter(User.email == username).first()
        
        if not user:
            log_debug(f"✗ Usuario no encontrado: {username}")
            return JSONResponse(
                status_code=401,
                content={"error": "Email o contraseña incorrectos"}
            )
        
        log_debug(f"✓ Usuario encontrado: {user.email}")

        # 3. Verificar contraseña
        log_debug("3. Verificando contraseña...")
        if not verify_password(password, user.password):
            log_debug("✗ Contraseña incorrecta")
            return JSONResponse(
                status_code=401,
                content={"error": "Email o contraseña incorrectos"}
            )
        
        log_debug("✓ Contraseña correcta")

        # 4. Generar token
        log_debug("4. Generando token...")
        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        log_debug("✓ Token generado")

        # 5. Preparar respuesta
        log_debug("5. Preparando respuesta...")
        response = RedirectResponse(url="/", status_code=302)  # 302 es para redirección temporal

        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=1800,
            path="/"
        )
        
        log_debug("✓ Cookie establecida")
        log_debug("✓ LOGIN EXITOSO")
        log_debug("="*50)
        
        return response

    except Exception as e:
        log_debug(f"¡ERROR CRÍTICO!: {str(e)}")
        log_debug(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": "Error interno del servidor"}
        )