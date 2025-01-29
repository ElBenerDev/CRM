from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List, Optional

from app.utils.db import get_db
from app.models.models import Lead, User
from app.schemas.schemas import LeadCreate, LeadResponse

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

lead_status = {
    'new': 'Nuevo',
    'contacted': 'Contactado',
    'qualified': 'Calificado',
    'converted': 'Convertido',
    'lost': 'Perdido'
}

@router.get("/leads", response_class=HTMLResponse)
async def leads_page(request: Request, db: Session = Depends(get_db)):
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            return RedirectResponse(url="/auth/login", status_code=302)
            
        current_user = db.query(User).filter(User.id == user_id).first()
        if not current_user:
            return RedirectResponse(url="/auth/login", status_code=302)

        leads = db.query(Lead).order_by(Lead.created_at.desc()).all()
        
        return templates.TemplateResponse(
            "leads.html",
            {
                "request": request,
                "user": {
                    "name": current_user.name,
                    "email": current_user.email,
                    "role": "Admin"
                },
                "active": "leads",
                "leads": leads,
                "status_options": lead_status
            }
        )
    except Exception as e:
        print(f"Error en leads_page: {str(e)}")
        return RedirectResponse(url="/auth/login", status_code=302)

@router.post("/api/leads/")
async def create_lead(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="No autenticado")

        new_lead = Lead(
            name=name,
            email=email,
            phone=phone,
            notes=notes,
            status='new',
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            created_by=user_id
        )
        
        db.add(new_lead)
        db.commit()
        db.refresh(new_lead)
        
        return JSONResponse(
            content={"message": "Lead creado exitosamente"},
            status_code=200
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/leads/")
async def create_lead(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    db: Session = Depends(get_db),
    request: Request = None,
    notes: Optional[str] = Form(None)
):
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="No autenticado")

        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead no encontrado")

        lead.status = status
        lead.updated_at = datetime.now(timezone.utc)
        db.commit()

        return JSONResponse(
            content={"message": "Estado del lead actualizado"},
            status_code=200
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))