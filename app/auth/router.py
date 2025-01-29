from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
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
        print(f"\n===== INTENTO DE LOGIN =====")
        print(f"👤 Usuario: {username}")
        
        user = db.query(User).filter(User.email == username).first()
        print(f"🔍 Usuario encontrado: {'✅' if user else '❌'}")
        
        if user and verify_password(password, user.password):
            print("✅ Contraseña verificada correctamente")
            request.session["user_id"] = str(user.id)
            return RedirectResponse(url="/", status_code=303)
        
        print("❌ Credenciales inválidas")
        return templates.TemplateResponse(
            "auth/login.html", 
            {"request": request, "error": "Credenciales inválidas"}
        )
    except Exception as e:
        print(f"❌ Error en login: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return templates.TemplateResponse(
            "auth/login.html", 
            {"request": request, "error": "Error de login"}
        )