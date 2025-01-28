from fastapi import Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.models.models import User

async def verify_auth(request: Request, call_next):
    if request.url.path.startswith("/auth/"):
        return await call_next(request)
        
    if request.url.path.startswith("/static/"):
        return await call_next(request)

    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/auth/login", status_code=302)

    # Obtener usuario de la DB
    db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)

    # Añadir usuario a request state
    request.state.user = user
    response = await call_next(request)
    return response