from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.models.models import User
from app.schemas.schemas import UserCreate, UserResponse, Token
from .utils import (
    authenticate_user, 
    create_access_token, 
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from datetime import timedelta
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapi.responses import JSONResponse

templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))
router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Modifica la ruta del token y agrega el manejo de cookies

@router.post("/token")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    print("Iniciando proceso de login")
    print(f"Email recibido: {form_data.username}")

    try:
        # Intenta autenticar al usuario
        user = authenticate_user(db, form_data.username, form_data.password)
        
        if not user:
            print("Autenticación fallida - Redirigiendo a login con error")
            response = RedirectResponse(
                url="/auth/login?error=credenciales_invalidas",
                status_code=303
            )
            return response

        # Usuario autenticado correctamente
        print(f"Usuario autenticado: {user.email}")
        access_token = create_access_token(data={"sub": user.email})
        
        # Crear respuesta de redirección
        response = RedirectResponse(
            url="/",
            status_code=303  # Cambiado a 303 See Other
        )
        
        # Establecer cookie
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=1800,
            path="/"
        )
        
        print("Redirigiendo al dashboard")
        return response
        
    except Exception as e:
        print(f"Error en login: {str(e)}")
        return RedirectResponse(
            url="/auth/login?error=error_servidor",
            status_code=303
        )
        
@router.get("/login")
async def login_page(request: Request, error: str = None):
    error_messages = {
        "credenciales_invalidas": "Usuario o contraseña incorrectos",
        "error_servidor": "Error del servidor, por favor intente más tarde"
    }
    
    return templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request,
            "error": error_messages.get(error, "") if error else ""
        }
    )
    
@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
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

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/auth/login")
    response.delete_cookie("access_token")
    return response