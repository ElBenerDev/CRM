from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.settings import settings
import time

# Configuración del engine con retry
def create_db_engine(retries=5, delay=5):
    for attempt in range(retries):
        try:
            engine = create_engine(
                settings.DATABASE_URL,
                pool_size=settings.DATABASE_POOL_SIZE,
                max_overflow=settings.DATABASE_MAX_OVERFLOW,
                pool_timeout=settings.DATABASE_POOL_TIMEOUT,
                pool_pre_ping=True  # Verifica la conexión antes de usarla
            )
            # Verificar conexión
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Conexión a la base de datos establecida correctamente")
            return engine
        except Exception as e:
            if attempt < retries - 1:
                print(f"❌ Intento {attempt + 1} fallido: {str(e)}")
                print(f"🔄 Reintentando en {delay} segundos...")
                time.sleep(delay)
            else:
                print("❌ No se pudo establecer conexión con la base de datos después de múltiples intentos")
                raise

# Crear el engine
engine = create_db_engine()

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
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✅ Verificación de conexión exitosa")
            return True
    except Exception as e:
        print(f"❌ Error en la verificación de conexión: {str(e)}")
        return False
    
def reset_db():
    try:
        if not verify_db_connection():
            raise Exception("No se pudo establecer conexión con la base de datos")
            
        # Importar los modelos aquí para evitar importación circular
        from app.models.models import Base
            
        # Desactivar las restricciones de clave foránea temporalmente
        with engine.connect() as conn:
            conn.execute(text("SET CONSTRAINTS ALL DEFERRED"))
            
        # Eliminar todas las tablas en el orden correcto
        Base.metadata.drop_all(bind=engine)
        
        # Crear todas las tablas nuevamente
        Base.metadata.create_all(bind=engine)
        
        print("✅ Base de datos reinicializada correctamente")
        return True
    except Exception as e:
        print(f"❌ Error al reinicializar la base de datos: {str(e)}")
        return False
    
__all__ = ['engine', 'SessionLocal', 'Base', 'get_db', 'verify_db_connection', 'reset_db']