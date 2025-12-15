from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, database, models, dependencies
from ..utils import crypto

router = APIRouter(
    tags=["Participant Onboarding"],
    dependencies=[Depends(dependencies.get_current_user)] # Requiere estar logueado
)

@router.post("/form", response_model=schemas.ProfileResponse)
def submit_registration_form(
    profile_data: schemas.ProfileCreate,
    current_user: models.User = Depends(dependencies.get_current_user),
    db: Session = Depends(database.get_db)
):
    # 1. Validar que no tenga ya un perfil
    if current_user.profile:
        raise HTTPException(status_code=400, detail="Profile already exists")

    # 2. Crear el perfil de negocio
    new_profile = models.ParticipantProfile(
        user_id=current_user.id,
        company_name=profile_data.company_name,
        legal_id=profile_data.legal_id,
        address=profile_data.address,
        contact_person=profile_data.contact_person,
        sector=profile_data.sector
    )

    # 3. Actualizar estado del usuario a REGISTERED
    # Según portal-backend.md, tras el formulario el usuario completa su registro
    current_user.status = models.UserStatus.REGISTERED

    db.add(new_profile)
    db.add(current_user) # Guardamos el cambio de estado
    db.commit()
    db.refresh(new_profile)

    return new_profile

@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(dependencies.get_current_user)):
    """Endpoint auxiliar para ver mis datos y mi estado actual"""
    return current_user


@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(dependencies.get_current_user)):
    return current_user


@router.get("/deployment", response_model=schemas.DeploymentSecretResponse)
def get_my_deployment_details(
    current_user: models.User = Depends(dependencies.get_current_user)
):
    if not current_user.deployment:
        raise HTTPException(status_code=404, detail="No deployment found. Wait for admin approval.")

    # Desciframos la API Key para que el usuario la vea
    decrypted_key = crypto.decrypt_value(current_user.deployment.api_key_encrypted)

    return {
        "did": current_user.deployment.did,
        "connector_url": current_user.deployment.connector_url,
        "identity_hub_url": current_user.deployment.identity_hub_url,
        "has_api_key": True,
        "api_key": decrypted_key # <--- El secreto revelado solo al dueño
    }