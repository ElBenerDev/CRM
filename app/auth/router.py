from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.utils.db import get_db
from app.models.models import User
from app.auth.utils import verify_password, get_password_hash
import traceback

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")


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
            # Cambia el status_code a 302 y asegúrate de que la URL sea correcta
            return RedirectResponse(
                url="/dashboard",  # Cambia esto según tu ruta correcta
                status_code=302
            )
            
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
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": str(e)}
        )
