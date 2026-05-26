from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core.database import get_session
from app.core.deps import get_current_active_user
from app.modules.usuarios.models import UsuarioPublic
from app.modules.direcciones.schemas import (
    DireccionCreate, DireccionPublic, DireccionUpdate, DireccionList,
)
from app.modules.direcciones.service import DireccionService

router = APIRouter()


def get_service(session: Annotated[Session, Depends(get_session)]) -> DireccionService:
    return DireccionService(session)


@router.post("/", response_model=DireccionPublic, status_code=status.HTTP_201_CREATED)
def create_direccion(
    data: DireccionCreate,
    svc: Annotated[DireccionService, Depends(get_service)],
    user: Annotated[UsuarioPublic, Depends(get_current_active_user)],
):
    return svc.create(data, usuario_id=user.id)


@router.get("/", response_model=DireccionList)
def list_mis_direcciones(
    svc: DireccionService = Depends(get_service),
    user: UsuarioPublic = Depends(get_current_active_user),
):
    return svc.list_mis_direcciones(usuario_id=user.id)


@router.get("/{direccion_id}", response_model=DireccionPublic)
def get_direccion(
    direccion_id: int,
    svc: DireccionService = Depends(get_service),
    user: UsuarioPublic = Depends(get_current_active_user),
):
    return svc.get_by_id(direccion_id, usuario_id=user.id)


@router.patch("/{direccion_id}", response_model=DireccionPublic)
def update_direccion(
    direccion_id: int,
    data: DireccionUpdate,
    svc: DireccionService = Depends(get_service),
    user: UsuarioPublic = Depends(get_current_active_user),
):
    return svc.update(direccion_id, data, usuario_id=user.id)


@router.delete("/{direccion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_direccion(
    direccion_id: int,
    svc: DireccionService = Depends(get_service),
    user: UsuarioPublic = Depends(get_current_active_user),
):
    svc.delete(direccion_id, usuario_id=user.id)
