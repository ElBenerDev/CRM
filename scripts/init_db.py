import os
import sys

# Añadir el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import Base, User
from app.auth.utils import get_password_hash
from config.settings import settings

def init_db():
    # Crear el engine
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        
        # Crear una sesión
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        # Verificar si ya existe un usuario admin
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        
        if not admin:
            # Crear usuario admin
            admin = User(
                email="admin@example.com",
                password=get_password_hash("admin123"),  # Cambia esta contraseña
                name="Admin",
                is_admin=True
            )
            db.add(admin)
            db.commit()
            print("✅ Usuario admin creado exitosamente")
        else:
            print("ℹ️ El usuario admin ya existe")
            
    except Exception as e:
        print(f"❌ Error inicializando la base de datos: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_db()