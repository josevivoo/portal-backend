from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import engine, Base, get_db, SessionLocal
from .routers import auth, admin, participant
from . import models, crud, schemas

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Dataspace Portal Backend")

# Incluir el router de autenticación
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(participant.router)

# --- Evento de Startup: Crear Admin inicial ---
@app.on_event("startup")
def create_initial_admin():
    db = SessionLocal()
    try:
        # Verificamos si ya existe algún usuario
        existing_user = db.query(models.User).first()
        if not existing_user:
            print("--- CREANDO ADMIN POR DEFECTO ---")
            admin_data = schemas.UserCreate(
                email="admin@dataspace.com",
                password="adminpassword"
            )
            crud.create_user(db, admin_data, role=models.UserRole.ADMIN)
            print("--- ADMIN CREADO: admin@dataspace.com / adminpassword ---")
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Portal Backend is running"}