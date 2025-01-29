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
        logger.info(f"Intento de login para: {username}")
        logger.info(f"Headers recibidos: {request.headers}")
        logger.info(f"Cookies recibidas: {request.cookies}")
        
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

        # Login exitoso - Configuración de sesión
        logger.info(f"Login exitoso para: {username}")
        
        # Limpiar y configurar sesión
        request.session.clear()
        request.session["user_id"] = str(user.id)
        request.session["authenticated"] = True
        
        logger.info(f"Sesión configurada: user_id={request.session.get('user_id')}")
        
        # Crear respuesta de redirección
        response = RedirectResponse(
            url="/dashboard",
            status_code=303
        )
        
        # Log de redirección
        logger.info(f"Redirigiendo a: {response.headers['location']}")
        
        return response

    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "error": "Error interno del servidor",
                "username": username
            },
            status_code=500
        )