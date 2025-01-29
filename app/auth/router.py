from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import traceback

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
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        print("\n===== INTENTO DE LOGIN =====")
        print(f"👤 Usuario: {username}")
        
        user = db.query(User).filter(User.email == username).first()
        print(f"🔍 Usuario encontrado: {'✅' if user else '❌'}")
        
        if user and verify_password(password, user.password):
            print("✅ Login exitoso")
            request.session["user_id"] = str(user.id)
            print(f"✅ Session ID establecido: {request.session['user_id']}")
            response = RedirectResponse(url="/dashboard", status_code=302)
            print(f"🔄 Redirigiendo a: {response.headers.get('location')}")
            return response
        
        print("❌ Credenciales inválidas")
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Credenciales inválidas"}
        )
    except Exception as e:
        print(f"❌ Error en login: {str(e)}")
        print(traceback.format_exc())  # Añade esto para ver el error completo
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": str(e)}
        )