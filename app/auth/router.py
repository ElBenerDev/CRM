from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.utils.db import get_db
from app.models.models import User
from app.auth.utils import verify_password

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    # Si ya está autenticado, redirigir al dashboard
    if request.session.get("user_id"):
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # Buscar usuario por email
        user = db.query(User).filter(User.email == email).first()
        
        # Verificar si el usuario existe y la contraseña es correcta
        if not user or not verify_password(password, user.password):
            return templates.TemplateResponse(
                "auth/login.html",
                {
                    "request": request,
                    "error": "Email o contraseña incorrectos"
                },
                status_code=400
            )
        
        # Si todo está bien, crear la sesión
        request.session["user_id"] = user.id
        request.session["user_name"] = user.name
        request.session["user_email"] = user.email
        
        # Actualizar último login
        user.last_login = datetime.now(timezone.utc)
        db.commit()
        
        # Redirigir al dashboard
        return RedirectResponse(url="/dashboard", status_code=302)
        
    except Exception as e:
        print(f"Error en login: {str(e)}")
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "error": "Error al iniciar sesión"
            },
            status_code=500
        )

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/auth/login", status_code=302)