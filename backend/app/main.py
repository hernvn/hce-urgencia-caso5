"""
Punto de entrada principal del Backend (FastAPI / ASGI) para el Caso 5:
Plataforma de Historia Clínica Electrónica (HCE) Interoperable y Telemedicina de Urgencia.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import Base, SessionLocal, engine
from app.routers.api_router import router as api_router
from app.seed import seed_initial_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Plataforma HCE Interoperable y Telemedicina de Urgencia — Caso 5",
    description=(
        "Implementación funcional del núcleo clínico (ADR-01 a ADR-08). "
        "Expone contratos REST/FHIR R4, autenticación JWT con RBAC de 4 roles, "
        "Patrón Strategy (Triage ESI + Resolución Dual de Conflictos CRDT/Concurrencia Optimista), "
        "Patrón Observer (Ledger de Auditoría Forense Hash-Encadenado SHA-256) y Patrón Repository."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Manejador global de errores de validación estructural (Pydantic v2 / FHIR R4).
    Entrega mensajes claros y trazables para la interfaz clínica.
    """
    error_messages = []
    sanitized_errors = []
    for err in exc.errors():
        loc = " -> ".join(str(x) for x in err.get("loc", []) if x != "body")
        msg = str(err.get("msg", "Valor inválido"))
        error_messages.append(f"[{loc}]: {msg}")
        sanitized_errors.append({"loc": loc, "msg": msg, "type": str(err.get("type", ""))})

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Error de validación clínica/estructural FHIR R4: " + " | ".join(error_messages),
            "validation_errors": sanitized_errors,
        },
    )


@app.get("/health", tags=["Infraestructura y Salud (ADR-07)"])
def health_check():
    return {
        "status": "UP",
        "service": "nucleo-asistencial-expediente-ordenes",
        "sla_target": "99.999%",
        "standards": ["HL7 FHIR R4", "HIPAA Security Rule", "WCAG 2.2 AAA"],
        "patterns_active": ["MVVM (Frontend)", "Strategy", "Observer", "Repository", "Transactional Outbox"],
    }


app.include_router(api_router)
