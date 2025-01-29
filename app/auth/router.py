# app/auth/router.py
import traceback
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

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # Log de intento de login
        logger.info(f"Intento de login para usuario: {username}")
        
        # Buscar usuario
        user = db.query(User).filter(User.email == username).first()
        
        if not user:
            logger.warning(f"Usuario no encontrado: {username}")
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Email o contraseña incorrectos"}
            )

        # Log del hash almacenado
        logger.info(f"Hash almacenado: {user.password}")
        
        # Verificar contraseña
        is_valid = verify_password(password, user.password)
        logger.info(f"Resultado de verificación de contraseña: {is_valid}")

        if not is_valid:
            logger.warning(f"Contraseña incorrecta para usuario: {username}")
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Email o contraseña incorrectos"}
            )

        # Log de login exitoso
        logger.info(f"Login exitoso para usuario: {username}")

        # Guardar en sesión
        request.session["user_id"] = str(user.id)
        request.session["user_email"] = user.email
        
        # Log de sesión guardada
        logger.info(f"Sesión guardada. user_id: {request.session.get('user_id')}, email: {request.session.get('user_email')}")
        
        # Redireccionar al dashboard con logs
        logger.info("Redirigiendo al dashboard...")
        response = RedirectResponse(url="/", status_code=303)
        return response

    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Error interno del servidor"}
        )