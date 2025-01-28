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

# Configuración de logging básica
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout
)

logger = logging.getLogger("auth")

@router.post("/token")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Logs directos a stdout para debug
    print("\n" + "="*50)
    print(f"INICIO LOGIN - Usuario: {username}")
    
    try:
        print("Verificando conexión a DB...")
        try:
            db.execute(text("SELECT 1"))
            print("✅ Conexión a DB verificada")
        except Exception as e:
            print(f"❌ Error de conexión a DB: {str(e)}")
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Error de conexión"},
                status_code=500
            )

        print("Buscando usuario...")
        user = db.query(User).filter(User.email == username).first()
        
        if not user:
            print("❌ Usuario no encontrado")
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Email o contraseña incorrectos"},
                status_code=401
            )
        
        print(f"✅ Usuario encontrado: {user.email}")
        
        print("Verificando contraseña...")
        if not verify_password(password, user.password):
            print("❌ Contraseña incorrecta")
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Email o contraseña incorrectos"},
                status_code=401
            )
        
        print("✅ Contraseña correcta")
        
        print("Generando token...")
        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        print("✅ Token generado")
        
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
        
        print("✅ Cookie establecida")
        print("✅ Login exitoso - Redirigiendo")
        print("="*50)
        
        return response
        
    except Exception as e:
        print("\n❌ ERROR EN LOGIN:")
        print(str(e))
        print("\nTraceback completo:")
        traceback.print_exc()
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Error del servidor"},
            status_code=500
        )

@router.get("/login")
async def login_page(request: Request):
    if request.cookies.get("access_token"):
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    print("\n" + "="*50)
    print(f"INICIO REGISTRO - Email: {user.email}")
    
    try:
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user:
            print("❌ Email ya registrado")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        print("Hasheando contraseña...")
        hashed_password = get_password_hash(user.password)
        
        print("Creando usuario...")
        db_user = User(
            email=user.email,
            password=hashed_password,
            name=user.name
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        print("✅ Usuario registrado correctamente")
        print("="*50)
        return db_user
        
    except HTTPException as he:
        print(f"❌ Error de validación: {str(he.detail)}")
        raise he
    except Exception as e:
        print("❌ Error en registro:")
        print(str(e))
        traceback.print_exc()
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar usuario: {str(e)}"
        )

@router.get("/logout")
async def logout():
    print("Iniciando logout...")
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie(
        key="access_token",
        path="/",
        secure=True,
        httponly=True
    )
    print("✅ Logout exitoso")
    return response