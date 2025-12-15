from sqlalchemy.orm import Session
from . import models, schemas, security

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate, role: models.UserRole = models.UserRole.PARTICIPANT):
    # 1. Hashear password
    hashed_password = security.get_password_hash(user.password)

    # 2. Crear instancia del modelo
    db_user = models.User(
        email=user.email,
        password_hash=hashed_password,
        role=role,
        status=models.UserStatus.PENDING # Estado inicial según portal-backend.md
    )

    # 3. Guardar en DB
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user