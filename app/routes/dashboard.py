from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from app.auth.utils import get_current_user
from sqlalchemy.orm import Session
from app.utils.db import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard")
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": current_user
        }
    )