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
        logger.info(f"Headers: {dict(request.headers)}")
        
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
        
        # Limpiar y configurar sesión
        request.session.clear()
        request.session["user_id"] = str(user.id)
        request.session["authenticated"] = True
        
        logger.info(f"Sesión configurada: {dict(request.session)}")
        
        # Crear respuesta
        response = RedirectResponse(
            url="/dashboard",
            status_code=303
        )
        
        # Asegurar que las cookies de sesión se establezcan
        if "session" not in request.cookies:
            logger.warning("Cookie de sesión no encontrada")
        
        logger.info(f"Cookies en la respuesta: {response.headers.get('set-cookie', 'No cookies')}")
        logger.info(f"Redirigiendo a: {response.headers.get('location')}")
        
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