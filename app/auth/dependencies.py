from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.models.models import User

async def get_current_user_id(
    request: Request,
    db: Session = Depends(get_db)
) -> int:
    if request is None:
        raise HTTPException(
            status_code=401,
            detail="No hay contexto de solicitud"
        )
    
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="No autenticado"
        )
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Usuario no encontrado"
        )
        
    return user_id