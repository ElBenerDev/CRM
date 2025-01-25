from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Obtener la URL de la base de datos de las variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("No se encontró la variable de entorno DATABASE_URL")

# Convertir postgres:// a postgresql:// (necesario para algunas versiones de SQLAlchemy)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

try:
    # Crear el engine de SQLAlchemy
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_pre_ping=True
    )
    
    print("✅ Conexión a la base de datos establecida correctamente")
except Exception as e:
    print(f"❌ Error al conectar a la base de datos: {str(e)}")
    raise

# Crear la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear la base declarativa
Base = declarative_base()

# Función para obtener la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para verificar la conexión
def verify_db_connection():
    try:
        db = SessionLocal()
        # Usar text() para la consulta SQL
        db.execute(text("SELECT 1"))
        print("✅ Verificación de conexión exitosa")
        return True
    except Exception as e:
        print(f"❌ Error en la verificación de conexión: {str(e)}")
        return False
    finally:
        db.close()