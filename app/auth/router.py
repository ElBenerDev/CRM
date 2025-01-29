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


@router.get("/login")
async def login_page(request: Request):
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
        
        # Verificar conexión a BD
        try:
            db.execute(text("SELECT 1"))
            print("✅ Conexión a BD verificada")
        except Exception as e:
            print(f"❌ Error de conexión a BD: {str(e)}")
            raise HTTPException(status_code=500, detail="Error de conexión a base de datos")

        # Buscar usuario
        user = db.query(User).filter(User.email == username).first()
        print(f"🔍 Usuario encontrado: {'✅' if user else '❌'}")
        
        if user and verify_password(password, user.password):
            print("✅ Login exitoso")
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
            {"request": request, "error": "Error en el servidor"}
        )