from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
# Configuración de conexión a PostgreSQL
DB_URL = os.getenv('URL_POSTGRES')

# Crear engine y pool de conexiones
engine = create_engine(
    DB_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

# Sesión thread-safe
SessionLocal = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))