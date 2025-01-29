from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.models.models import User
from app.auth.utils import verify_password

router = APIRouter()
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
        print("\n===== INTENTO DE LOGIN =====")
        print(f"👤 Usuario: {username}")
        
        user = db.query(User).filter(User.email == username).first()
        print(f"🔍 Usuario encontrado: {'✅' if user else '❌'}")
        
        if user and verify_password(password, user.password):
            print("✅ Login exitoso")
            request.session["user_id"] = str(user.id)
            print(f"✅ Session ID establecido: {request.session['user_id']}")
            
            # Asegúrate de que la redirección use status_code=303
            response = RedirectResponse(
                url="/dashboard",
                status_code=303  # Cambiado de 302 a 303 para POST -> GET
            )
            print(f"🔄 Redirigiendo a: {response.headers.get('location')}")
            return response
        
        print("❌ Credenciales inválidas")
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "error": "Credenciales inválidas"
            },
            status_code=400
        )
    except Exception as e:
        print(f"❌ Error en login: {str(e)}")
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "error": str(e)
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