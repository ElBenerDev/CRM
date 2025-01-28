from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from starlette.middleware.sessions import SessionMiddleware
import os

from app.utils.db import get_db
from app.models.models import User
from .utils import verify_password

router = APIRouter(prefix="/auth", tags=["auth"])
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "app", "templates"))

@router.post("/token")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
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
        
        # Guardar en sesión
        request.session["user_id"] = user.id
        request.session["user_email"] = user.email
        
        # Redireccionar al dashboard
        response = RedirectResponse(url="/", status_code=302)
        return response

    except Exception as e:
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "error": "Error interno del servidor"
            },
            status_code=500
        )