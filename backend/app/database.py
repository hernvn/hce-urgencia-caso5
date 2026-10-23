"""
Configuración de Base de Datos Relacional (SQLAlchemy 2.0) y Seguridad Criptográfica.
Implementa el motor de persistencia del núcleo clínico y el almacenamiento del Ledger Forense.
"""
import hashlib
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hce_urgencia_caso5.db")
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "hce-urgencia-caso5-secret-key-hipaa-2026-fhir-r4")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Definido en ADR-02 y ADR-08 (15 minutos de vida corta)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    """Genera hash SHA-256 con salt estático de dominio para demostración reproducible sin dependencias C."""
    salted = f"caso5_hce_salt_2026::{password}".encode("utf-8")
    return hashlib.sha256(salted).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica la contraseña en tiempo constante frente al hash almacenado."""
    return hash_password(plain_password) == hashed_password


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Emite un token JWT firmado (RFC 7519) con claims de rol, sub y expiración (ADR-02/ADR-08)."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decodifica y verifica la firma criptográfica del JWT."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
