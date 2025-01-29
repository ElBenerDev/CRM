# app/auth/router.py
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.models.models import User
from .utils import verify_password
from app.utils.logging_config import logger

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.post("/token")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # Imprimir información de depuración
        print(f"Intento de login para: {username}")
        
        # Buscar usuario
        user = db.query(User).filter(User.email == username).first()
        
        if not user:
            print("Usuario no encontrado")
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Email o contraseña incorrectos"}
            )

        if not verify_password(password, user.password):
            print("Contraseña incorrecta")
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Email o contraseña incorrectos"}
            )

        print("Login exitoso")
        
        # Guardar en sesión
        request.session["user_id"] = str(user.id)
        request.session["user_email"] = user.email
        
        # Redireccionar al dashboard
        return RedirectResponse(url="/", status_code=303)

    except Exception as e:
        print(f"Error en login: {str(e)}")
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Error interno del servidor"}
        )