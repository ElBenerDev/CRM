from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
import os

# Configuración de la base de datos
DB_USER = "neondb_owner"
DB_PASSWORD = "npg_mTJhLZ5FtRA3"
DB_HOST = "ep-little-term-a8x9ojn0-pooler.eastus2.azure.neon.tech"
DB_NAME = "neondb"

# Crear URL de conexión
DATABASE_URL = f"postgresql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}/{DB_NAME}"

# Crear engine
engine = create_engine(DATABASE_URL)

def fix_created_at():
    print("🔄 Iniciando migración de created_at...")
    try:
        with engine.connect() as connection:
            # Actualizar registros existentes
            print("📝 Actualizando registros con created_at NULL...")
            connection.execute(text("""
                UPDATE patients 
                SET created_at = CURRENT_TIMESTAMP 
                WHERE created_at IS NULL
            """))
            
            # Modificar la columna
            print("🔧 Modificando la estructura de la columna...")
            connection.execute(text("""
                ALTER TABLE patients 
                ALTER COLUMN created_at SET NOT NULL,
                ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP
            """))
            
            connection.commit()
            print("✅ Migración completada exitosamente")
            
    except Exception as e:
        print(f"❌ Error durante la migración: {str(e)}")
        raise

if __name__ == "__main__":
    fix_created_at()