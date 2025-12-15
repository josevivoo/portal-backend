import enum
import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Enum, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# --- Enums definidos para el estado del usuario y credenciales ---
class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    PARTICIPANT = "PARTICIPANT"

class UserStatus(str, enum.Enum):
    PENDING = "PENDING"       # Estado inicial tras invitación
    REGISTERED = "REGISTERED" # Tras completar formulario
    DEPLOYING = "DEPLOYING"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"


# --- 1. Usuario (User) ---
# Responsabilidad: Autenticación y Ciclo de Vida
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.PARTICIPANT)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING)
    activation_token = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    profile = relationship("ParticipantProfile", back_populates="user", uselist=False)
    deployment = relationship("DataspaceDeployment", back_populates="user", uselist=False)

# --- 2. Perfil del Participante (ParticipantProfile) ---
# Responsabilidad: Información de Negocio
class ParticipantProfile(Base):
    __tablename__ = "participant_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)

    company_name = Column(String, nullable=False)
    legal_id = Column(String, nullable=False)
    address = Column(JSON, nullable=True)
    contact_person = Column(String, nullable=True)
    sector = Column(String, nullable=True)

    user = relationship("User", back_populates="profile")

# --- 3. Infraestructura Dataspace (DataspaceDeployment) ---
# Responsabilidad: Datos técnicos de conexión y secretos
class DataspaceDeployment(Base):
    __tablename__ = "dataspace_deployments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)

    did = Column(String, unique=True, nullable=True)
    connector_url = Column(String, nullable=True)
    management_url = Column(String, nullable=True)
    identity_hub_url = Column(String, nullable=True)

    api_key_encrypted = Column(String, nullable=True)
    encryption_iv = Column(String, nullable=True)
    last_rotation = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="deployment")

