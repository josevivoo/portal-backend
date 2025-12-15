import secrets
import uuid
import string
from ..utils import crypto
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, database, models, crud, dependencies, security
from sqlalchemy.sql import func

router = APIRouter(
    prefix="/admin",
    tags=["Admin Management"],
    dependencies=[Depends(dependencies.get_current_admin)] # Protege todo el router
)

def generate_temp_password(length=12):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))

@router.post("/invite", response_model=schemas.InviteResponse)
def invite_participant(
    invite_data: schemas.UserInvite,
    db: Session = Depends(database.get_db)
):
    # 1. Verificar si el usuario ya existe
    user = crud.get_user_by_email(db, email=invite_data.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2. Generar contraseña temporal
    temp_password = generate_temp_password()
    hashed_password = security.get_password_hash(temp_password)

    # 3. Crear usuario con estado PENDING
    # Nota: Usamos User directamente aquí o una función crud específica si prefieres
    new_user = models.User(
        email=invite_data.email,
        password_hash=hashed_password,
        role=models.UserRole.PARTICIPANT,
        status=models.UserStatus.PENDING
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 4. Simular envío de correo (Aquí integrarías SMTP más tarde)
    print(f"============================================")
    print(f" EMAIL A: {new_user.email}")
    print(f" ASUNTO: Invitación al Dataspace")
    print(f" MENSAJE: Tu usuario es {new_user.email} y tu contraseña temporal es: {temp_password}")
    print(f"============================================")

    return {
        "email": new_user.email,
        "temp_password": temp_password,
        "message": "User invited successfully. Email sent (simulated)."
    }

@router.post("/accept/{user_id}", response_model=schemas.DeploymentResponse)
def accept_participant_and_deploy(
    user_id: uuid.UUID,
    db: Session = Depends(database.get_db)
):
    # 1. Obtener usuario
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Verificar estado (Solo REGISTERED puede ser aceptado)
    if user.status != models.UserStatus.REGISTERED:
        raise HTTPException(status_code=400, detail=f"User is in {user.status} state, expected REGISTERED")

    # 3. Simular Despliegue de Infraestructura (Identity Hub + Connector)
    # En un entorno real, aquí llamarías a la API de Kubernetes o Helm
    generated_did = f"did:web:dataspace:{str(user_id)[:8]}"
    connector_address = f"http://connector-{str(user_id)[:8]}.dataspace.svc"

    # Generar API Key aleatoria para el conector
    raw_api_key = secrets.token_urlsafe(32)
    encrypted_key = crypto.encrypt_value(raw_api_key)

    # 4. Guardar datos en DataspaceDeployment (Tabla de Infraestructura)
    deployment = models.DataspaceDeployment(
        user_id=user.id,
        did=generated_did,
        connector_url=connector_address,
        management_url=f"{connector_address}/management",
        identity_hub_url=f"http://identity-hub-{str(user_id)[:8]}.dataspace.svc",
        api_key_encrypted=encrypted_key,
        encryption_iv="fernet_default", # Fernet maneja el IV internamente
        last_rotation=func.now()
    )

    # 5. Actualizar estado del usuario a ACTIVE
    user.status = models.UserStatus.ACTIVE

    db.add(deployment)
    db.add(user)
    db.commit()
    db.refresh(deployment)

    # (Opcional) Imprimimos la API Key por consola para que la veas (ya que no la devolvemos en API)
    print(f"============================================")
    print(f" DESPLIEGUE FINALIZADO PARA: {user.email}")
    print(f" API KEY (GUARDAR AHORA): {raw_api_key}")
    print(f" DID: {generated_did}")
    print(f"============================================")

    return deployment