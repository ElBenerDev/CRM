from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.models.models import User
from app.auth.utils import verify_password
import logging

router = APIRouter(prefix="/auth", tags=["auth"])  
templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request,
            "username": request.query_params.get("username", "")
        }
    )

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # Log de inicio
        logger.info(f"Intento de login para: {username}")
        
        # Buscar usuario
        user = db.query(User).filter(User.email == username).first()
        if not user:
            logger.warning(f"Usuario no encontrado: {username}")
            return templates.TemplateResponse(
                "auth/login.html",
                {
                    "request": request,
                    "error": "Usuario o contraseña incorrectos",
                    "username": username
                },
                status_code=401
            )

        # Verificar contraseña
        if not verify_password(password, user.password):
            logger.warning(f"Contraseña incorrecta para: {username}")
            return templates.TemplateResponse(
                "auth/login.html",
                {
                    "request": request,
                    "error": "Usuario o contraseña incorrectos",
                    "username": username
                },
                status_code=401
            )

        # Login exitoso
        logger.info(f"Login exitoso para: {username}")
        request.session.clear()
        request.session["user_id"] = str(user.id)
        
        # Redireccionar
        response = RedirectResponse(url="/dashboard", status_code=303)
        logger.info(f"Redirigiendo a: {response.headers.get('location')}")
        return response

    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "error": "Error interno del servidor",
                "username": username
            },
            status_code=500
        )