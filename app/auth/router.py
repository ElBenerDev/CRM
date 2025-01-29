from fastapi import APIRouter, Depends, Request, Response, Form, HTTPException, status
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
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request}
    )

@router.post("/login")
async def login(
    request: Request,
    response: Response,  # Añade esto
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
            request.session["authenticated"] = True  # Añade esto
            print(f"✅ Session ID establecido: {request.session['user_id']}")
            
            # Modifica la redirección
            response = RedirectResponse(
                url="/dashboard",
                status_code=status.HTTP_302_FOUND
            )
            response.headers["Location"] = "/dashboard"
            print(f"🔄 Redirigiendo a: {response.headers.get('location')}")
            return response
        
        print("❌ Credenciales inválidas")
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Credenciales inválidas"},
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        print(f"❌ Error en login: {str(e)}")
        print(f"Traceback completo: {traceback.format_exc()}")
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": f"Error en el servidor: {str(e)}"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )