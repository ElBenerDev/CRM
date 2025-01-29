from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard")
async def dashboard(request: Request):
    if not request.session.get("user_id"):
        return RedirectResponse(url="/auth/login", status_code=302)
    return templates.TemplateResponse("dashboard.html", {"request": request})