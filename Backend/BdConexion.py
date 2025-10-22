# para que sirve sqlalchemy
# ORM = Object Relational Mapping
# permite mapear tablas de bases de datos a clases de Python
# y objetos de Python a filas de tablas de bases de datos
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
# que hace dotenv
# permite cargar variables de entorno desde un archivo .env
from dotenv import load_dotenv
import os

# Cargar .env
load_dotenv()

# Leer configuración de base de datos desde variables de entorno
# En Docker, DATABASE_URL viene del docker-compose.yml
# En desarrollo local, se construye desde las variables individuales
DB_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+psycopg2://{os.getenv('POSTGRES_USER', 'postgres')}:"
    f"{os.getenv('POSTGRES_PASSWORD', os.getenv('DataBasePassword', 'tallerdedi1'))}@"
    f"{os.getenv('DB_HOST', 'localhost')}:5432/"
    f"{os.getenv('POSTGRES_DB', 'Airfresh')}"
)

# Crear el engine y la sesión
engine = create_engine(DB_URL, pool_pre_ping=True, future=True)
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()