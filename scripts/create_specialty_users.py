import sys
import os
from pathlib import Path
from datetime import datetime

# Agregar el directorio raíz al PATH
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.db.models.user import User, SpecialtyType

def create_specialty_users():
    db = SessionLocal()
    current_time = datetime.utcnow()
    
    try:
        # Usuario Dentista (mantenemos el existente si ya existe)
        dental_user = db.query(User).filter(User.email == "dental@clinic.com").first()
        if not dental_user:
            dental_user = User(
                email="dental@clinic.com",
                name="Dr. Dental",
                password=get_password_hash("dental123"),
                specialty=SpecialtyType.DENTAL,
                clinic_name="Clínica Dental",
                professional_license="DEN123",
                created_at=current_time,
                updated_at=current_time
            )
            db.add(dental_user)

        # Usuario Oftalmólogo
        eye_user = db.query(User).filter(User.email == "eye@clinic.com").first()
        if not eye_user:
            eye_user = User(
                email="eye@clinic.com",
                name="Dr. Oftalmólogo",
                password=get_password_hash("eye123"),
                specialty=SpecialtyType.OPHTHALMOLOGY,
                clinic_name="Clínica Oftalmológica",
                professional_license="OPH123",
                created_at=current_time,
                updated_at=current_time
            )
            db.add(eye_user)

        # Usuario Médico General
        general_user = db.query(User).filter(User.email == "general@clinic.com").first()
        if not general_user:
            general_user = User(
                email="general@clinic.com",
                name="Dr. General",
                password=get_password_hash("gen123"),
                specialty=SpecialtyType.GENERAL_MEDICINE,
                clinic_name="Clínica General",
                professional_license="GEN123",
                created_at=current_time,
                updated_at=current_time
            )
            db.add(general_user)

        db.commit()
        print("✅ Usuarios creados exitosamente")

    except Exception as e:
        print(f"❌ Error creando usuarios: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_specialty_users()