from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional

from app.utils.db import get_db
from app.models.models import User
from app.auth.utils import get_password_hash, verify_password

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, db: Session = Depends(get_db)):
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            return RedirectResponse(url="/auth/login", status_code=302)
            
        current_user = db.query(User).filter(User.id == user_id).first()
        if not current_user:
            return RedirectResponse(url="/auth/login", status_code=302)

        return templates.TemplateResponse(
            "settings.html",
            {
                "request": request,
                "user": {
                    "name": current_user.name,
                    "email": current_user.email,
                    "role": "Admin"
                },
                "active": "settings"
            }
        )
    except Exception as e:
        print(f"Error en settings_page: {str(e)}")
        return RedirectResponse(url="/auth/login", status_code=302)

@router.post("/api/settings/change-password")
async def change_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
    request: Request = None
):
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="No autenticado")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        if not verify_password(current_password, user.password):
            raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")

        if new_password != confirm_password:
            raise HTTPException(status_code=400, detail="Las contraseñas no coinciden")

        user.password = get_password_hash(new_password)
        user.updated_at = datetime.now(timezone.utc)
        db.commit()

        return JSONResponse(
            content={"message": "Contraseña actualizada exitosamente"},
            status_code=200
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/settings/update-profile")
async def update_profile(
    name: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_db),
    request: Request = None
):
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="No autenticado")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        user.name = name
        user.email = email
        user.updated_at = datetime.now(timezone.utc)
        db.commit()

        return JSONResponse(
            content={"message": "Perfil actualizado exitosamente"},
            status_code=200
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))