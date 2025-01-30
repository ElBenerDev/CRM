import sys
import os
from pathlib import Path

# Añadir el directorio raíz al PATH
sys.path.append(str(Path(__file__).parent.parent))

from app.db.session import engine, Base
from app.db.models.user import User
from app.db.models.patient import Patient
from app.db.models.appointment import Appointment
from app.db.models.lead import Lead
from app.core.security import get_password_hash
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

def init_db():
    print("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Verificar si ya existe un usuario admin
        admin = db.query(User).filter(User.email == "admin@admin.com").first()
        if not admin:
            print("Creando usuario administrador...")
            admin_user = User(
                email="admin@admin.com",
                name="Administrador",
                password=get_password_hash("admin123"),
                is_active=True,
                is_admin=True
            )
            db.add(admin_user)
            db.commit()
            print("Usuario administrador creado exitosamente")
        
        # Crear algunos datos de ejemplo
        if db.query(Patient).count() == 0:
            print("Creando datos de ejemplo...")
            # Crear algunos pacientes de ejemplo
            patients = [
                Patient(
                    name="Juan Pérez",
                    email="juan@example.com",
                    phone="123456789",
                    address="Calle Principal 123",
                    notes="Paciente regular"
                ),
                Patient(
                    name="María García",
                    email="maria@example.com",
                    phone="987654321",
                    address="Avenida Central 456",
                    notes="Paciente nuevo"
                )
            ]
            db.add_all(patients)
            db.commit()
            print("Datos de ejemplo creados exitosamente")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Iniciando configuración de la base de datos...")
    init_db()
    print("Configuración completa")