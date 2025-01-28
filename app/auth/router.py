from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi.security import OAuth2PasswordBearer
from starlette.middleware.sessions import SessionMiddleware
import os
from app.core.config import settings
from app.utils.logging_config import logger

from app.utils.db import get_db
from app.models.models import User
from .utils import verify_password

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)

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
    logger.info("Inicio de proceso de login")
    logger.info(f"Usuario: {username}")

    try:
        # Verificar conexión a DB
        try:
            db.execute(text("SELECT 1"))
            logger.info("Conexión a DB OK")
        except Exception as e:
            logger.error(f"Error de conexión: {str(e)}")
            return templates.TemplateResponse(
                "auth/login.html",
                {
                    "request": request,
                    "error": "Error de conexión a la base de datos"
                },
                status_code=500
            )

        # Buscar usuario
        user = db.query(User).filter(User.email == username).first()
        
        if not user or not verify_password(password, user.password):
            return templates.TemplateResponse(
                "auth/login.html",
                {
                    "request": request,
                    "error": "Email o contraseña incorrectos"
                },
                status_code=401
            )

        # Limpiar sesión anterior si existe
        request.session.clear()
        
        # Guardar en sesión
        request.session["user_id"] = str(user.id)
        request.session["user_email"] = user.email
        
        # Forzar guardado de sesión
        await request.session.save()
        
        # Redireccionar al dashboard con headers específicos
        response = RedirectResponse(url="/", status_code=302)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "error": "Error interno del servidor"
            },
            status_code=500
        )