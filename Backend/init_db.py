"""
Script para inicializar la base de datos creando todas las tablas.
"""
from Backend.BdConexion import engine, Base
from Backend.models.mediciones import Medicion

def init_database():
    """Crea todas las tablas definidas en los modelos."""
    print("🔧 Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas exitosamente!")
    
    # Mostrar las tablas creadas
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"📋 Tablas en la base de datos: {tables}")

if __name__ == "__main__":
    init_database()
