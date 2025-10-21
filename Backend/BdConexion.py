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


# Leer contraseña desde variable de entorno
db_password = os.getenv("DataBasePassword")

# Construir la URL de conexión a Postgres local
DB_URL = f"postgresql+psycopg2://postgres:{db_password}@localhost:5432/Airfresh"

# Crear el engine y la sesión
engine = create_engine(DB_URL, pool_pre_ping=True, future=True)
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()