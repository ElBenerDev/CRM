from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional, Union
from datetime import datetime
from app.models.models import Patient, Appointment, Lead, AppointmentStatus, LeadStatus
from fastapi import HTTPException

class CRMService:
    def __init__(self, db: Session):
        self.db = db

    # Patient Services
    def create_patient(self, patient_data: dict) -> Patient:
        db_patient = Patient(**patient_data.dict())
        self.db.add(db_patient)
        self.db.commit()
        self.db.refresh(db_patient)
        return db_patient

    def get_patients(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[Patient]:
        query = self.db.query(Patient)
        if search:
            search_filter = or_(
                Patient.name.ilike(f"%{search}%"),
                Patient.email.ilike(f"%{search}%"),
                Patient.phone.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        return query.offset(skip).limit(limit).all()

    def get_patient(self, patient_id: int) -> Optional[Patient]:
        return self.db.query(Patient).filter(Patient.id == patient_id).first()

    def update_patient(self, patient_id: int, patient_data: dict) -> Optional[Patient]:
        db_patient = self.get_patient(patient_id)
        if db_patient:
            for key, value in patient_data.dict(exclude_unset=True).items():
                setattr(db_patient, key, value)
            self.db.commit()
            self.db.refresh(db_patient)
        return db_patient

    def delete_patient(self, patient_id: int) -> bool:
        db_patient = self.get_patient(patient_id)
        if db_patient:
            self.db.delete(db_patient)
            self.db.commit()
            return True
        return False

    # Appointment Services
    def create_appointment(self, appointment_data: dict) -> Appointment:
        if not self.get_patient(appointment_data.patient_id):
            raise HTTPException(status_code=404, detail="Patient not found")
            
        db_appointment = Appointment(**appointment_data.dict())
        self.db.add(db_appointment)
        self.db.commit()
        self.db.refresh(db_appointment)
        return db_appointment

    def get_appointments(
        self,
        skip: int = 0,
        limit: int = 100,
        patient_id: Optional[int] = None,
        status: Optional[AppointmentStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Appointment]:
        query = self.db.query(Appointment)
        
        filters = []
        if patient_id:
            filters.append(Appointment.patient_id == patient_id)
        if status:
            filters.append(Appointment.status == status)
        if start_date:
            filters.append(Appointment.date >= start_date)
        if end_date:
            filters.append(Appointment.date <= end_date)
            
        if filters:
            query = query.filter(and_(*filters))
            
        return query.offset(skip).limit(limit).all()

    # Lead Services
    def create_lead(self, lead_data: dict) -> Lead:
        if not self.get_patient(lead_data.patient_id):
            raise HTTPException(status_code=404, detail="Patient not found")
            
        db_lead = Lead(**lead_data.dict())
        self.db.add(db_lead)
        self.db.commit()
        self.db.refresh(db_lead)
        return db_lead

    def get_leads(
        self,
        skip: int = 0,
        limit: int = 100,
        patient_id: Optional[int] = None,
        status: Optional[LeadStatus] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ) -> List[Lead]:
        query = self.db.query(Lead)
        
        filters = []
        if patient_id:
            filters.append(Lead.patient_id == patient_id)
        if status:
            filters.append(Lead.status == status)
        if min_value is not None:
            filters.append(Lead.expected_value >= min_value)
        if max_value is not None:
            filters.append(Lead.expected_value <= max_value)
            
        if filters:
            query = query.filter(and_(*filters))
            
        return query.offset(skip).limit(limit).all()