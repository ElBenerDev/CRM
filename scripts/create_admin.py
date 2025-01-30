import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.db.models.user import User
from app.core.security import get_password_hash

def create_admin_user():
    db = SessionLocal()
    try:
        # Verificar si ya existe un admin
        admin = db.query(User).filter(User.email == "admin@admin.com").first()
        
        if not admin:
            admin = User(
                email="admin@admin.com",
                name="Admin",
                password=get_password_hash("admin123"),
                is_active=True,
                is_admin=True
            )
            db.add(admin)
            db.commit()
            print("✅ Usuario admin creado correctamente")
        else:
            print("ℹ️ El usuario admin ya existe")
    except Exception as e:
        print(f"❌ Error creando usuario admin: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()