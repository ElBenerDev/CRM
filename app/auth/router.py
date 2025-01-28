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

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

# app/auth/router.py
# Modifica la ruta del token y agrega el manejo de cookies

@router.post("/token")
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    print(f"Recibiendo solicitud POST en /auth/token")
    print(f"Datos recibidos - username: {form_data.username}")
    
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
        
        if not user:
            print("Autenticación fallida - Usuario no encontrado o contraseña incorrecta")
            return templates.TemplateResponse(
                "auth/login.html",
                {
                    "request": request,
                    "error": "Credenciales inválidas"
                },
                status_code=401
            )

        print(f"Usuario autenticado correctamente: {user.email}")
        access_token = create_access_token(data={"sub": user.email})
        
        response = RedirectResponse(url="/", status_code=302)
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
        print(f"Error en el proceso de login: {str(e)}")
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "error": f"Error del servidor: {str(e)}"
            },
            status_code=500
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