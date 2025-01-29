# app/auth/router.py
import traceback
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.models.models import User
from .utils import verify_password
from app.utils.logging_config import logger

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
        user = db.query(User).filter(User.email == username).first()
        
        if user and user.password == password:  # Simple password check for now
            request.session["user_id"] = str(user.id)
            return RedirectResponse(url="/dashboard", status_code=303)
        
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Invalid credentials"}
        )
    except Exception as e:
        print(f"Login error: {e}")
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Server error"}
        )