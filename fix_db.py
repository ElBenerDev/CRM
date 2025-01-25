from sqlalchemy import create_engine, text
from datetime import datetime

# Configuración de la base de datos
DATABASE_URL = "postgresql://neondb_owner:npg_mTJhLZ5FtRA3@ep-little-term-a8x9ojn0-pooler.eastus2.azure.neon.tech/neondb"

def fix_database():
    print("🔄 Iniciando corrección de la base de datos...")
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Primero actualizar registros nulos
            conn.execute(text("""
                UPDATE patients 
                SET created_at = CURRENT_TIMESTAMP 
                WHERE created_at IS NULL
            """))
            
            # Luego modificar la columna
            conn.execute(text("""
                ALTER TABLE patients 
                ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP,
                ALTER COLUMN created_at SET NOT NULL
            """))
            
            conn.commit()
            print("✅ Base de datos actualizada correctamente")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise

if __name__ == "__main__":
    fix_database()