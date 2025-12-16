import os
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import engine, Base, get_db, SessionLocal
from .routers import auth, admin, participant
from . import models, crud, schemas

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Dataspace Portal Backend")

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(participant.router)

# --- Evento de Startup: Crear Admin inicial ---
@app.on_event("startup")
def create_initial_admin():
    db = SessionLocal()
    try:
        existing_user = db.query(models.User).first()
        if not existing_user:
            # LEER DEL ENTORNO (seguro)
            admin_email = os.getenv("ADMIN_EMAIL")
            admin_password = os.getenv("ADMIN_PASSWORD")

            # Validación de seguridad: Si no hay variables, no creamos nada por defecto inseguro
            if not admin_email or not admin_password:
                print("⚠️  ADVERTENCIA: ADMIN_EMAIL o ADMIN_PASSWORD no configurados en .env. No se creó el admin.")
                return

            print("--- CREANDO ADMIN DESDE VARIABLES DE ENTORNO ---")
            admin_data = schemas.UserCreate(
                email=admin_email,
                password=admin_password
            )
            crud.create_user(db, admin_data, role=models.UserRole.ADMIN)
            print(f"--- ADMIN CREADO: {admin_email} ---")
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Portal Backend is running"}