from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.core.deps import get_current_active_user, require_role
from app.modules.usuarios.models import UsuarioPublic
from app.modules.unidad_medida.schemas import (
    UnidadMedidaCreate, UnidadMedidaPublic, UnidadMedidaUpdate, UnidadMedidaList,
)
from app.modules.unidad_medida.service import UnidadMedidaService

router = APIRouter()


def get_service(session: Annotated[Session, Depends(get_session)]) -> UnidadMedidaService:
    return UnidadMedidaService(session)


@router.post("/", response_model=UnidadMedidaPublic, status_code=status.HTTP_201_CREATED)
def create_unidad(
    data: UnidadMedidaCreate,
    svc: Annotated[UnidadMedidaService, Depends(get_service)],
    _admin: Annotated[UsuarioPublic, Depends(require_role(["ADMIN"]))],
):
    return svc.create(data)


@router.get("/", response_model=UnidadMedidaList)
def list_unidades(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    svc: UnidadMedidaService = Depends(get_service),
    _user: UsuarioPublic = Depends(get_current_active_user),
):
    return svc.get_all(offset=offset, limit=limit)


@router.get("/{unidad_id}", response_model=UnidadMedidaPublic)
def get_unidad(
    unidad_id: int,
    svc: UnidadMedidaService = Depends(get_service),
    _user: UsuarioPublic = Depends(get_current_active_user),
):
    return svc.get_by_id(unidad_id)


@router.patch("/{unidad_id}", response_model=UnidadMedidaPublic)
def update_unidad(
    unidad_id: int,
    data: UnidadMedidaUpdate,
    svc: UnidadMedidaService = Depends(get_service),
    _admin: UsuarioPublic = Depends(require_role(["ADMIN"])),
):
    return svc.update(unidad_id, data)


@router.delete("/{unidad_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_unidad(
    unidad_id: int,
    svc: UnidadMedidaService = Depends(get_service),
    _admin: UsuarioPublic = Depends(require_role(["ADMIN"])),
):
    svc.delete(unidad_id)
