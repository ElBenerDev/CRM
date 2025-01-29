from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.models.models import User
from app.auth.utils import verify_password
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="app/templates")

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request}
    )

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Intento de login para usuario: {username}")
        
        # Buscar usuario
        user = db.query(User).filter(User.email == username).first()
        logger.info(f"Usuario encontrado: {'Si' if user else 'No'}")
        
        if user and verify_password(password, user.password):
            # Guardar en sesión como string
            request.session["user_id"] = str(user.id)
            logger.info(f"Login exitoso para usuario {username}")
            logger.info(f"Session ID guardado: {request.session.get('user_id')}")
            
            # Usar código 303 para POST -> GET
            response = RedirectResponse(
                url="/dashboard",
                status_code=303
            )
            logger.info(f"Redirigiendo a: {response.headers.get('location')}")
            return response
        
        logger.warning(f"Login fallido para usuario {username}")
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "error": "Credenciales inválidas"
            },
            status_code=400
        )
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

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(
        url="/auth/login",
        status_code=303  # También usar 303 aquí
    )