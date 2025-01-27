import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.utils.db import SessionLocal
from app.models.models import User
from app.auth.utils import get_password_hash

def create_admin_user(email: str, password: str, name: str):
    db = SessionLocal()
    try:
        # Verificar si el usuario ya existe
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"El usuario {email} ya existe")
            return

        # Crear nuevo usuario admin
        hashed_password = get_password_hash(password)
        admin_user = User(
            email=email,
            password=hashed_password,
            name=name,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        print(f"Usuario administrador {email} creado exitosamente")
    
    except Exception as e:
        print(f"Error creando usuario admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user(
        email="admin@example.com",
        password="admin123",  # Cambiar en producción
        name="Administrador"
    )