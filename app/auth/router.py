from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.models.models import User
from app.auth.utils import verify_password
import logging
from starlette.status import HTTP_303_SEE_OTHER
import traceback

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)

@router.get("/login", response_class=HTMLResponse, name="login")
async def login_page(request: Request):
    logger.info("Accediendo a página de login")
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request}
    )

@router.post("/login", name="login_post")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Validando usuario: {username}")
        
        # Buscar usuario
        user = db.query(User).filter(User.email == username).first()
        if not user:
            logger.error("Usuario no encontrado en la base de datos")
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Usuario no existe"},
                status_code=401
            )

        # Verificar contraseña
        if not verify_password(password, user.password):
            logger.error("Contraseña incorrecta")
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Contraseña inválida"},
                status_code=401
            )

        # Configurar sesión
        request.session.clear()
        request.session["user_id"] = str(user.id)
        request.session["authenticated"] = True
        logger.info("Sesión configurada correctamente")

        # Redirigir al dashboard
        response = RedirectResponse(url="/dashboard", status_code=303)
        logger.info(f"Cookie de sesión: {request.session}")
        return response

    except Exception as e:
        logger.error(f"Error crítico: {str(e)}")
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Error interno del servidor"},
            status_code=500
        )