from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.core.deps import get_current_active_user, require_role
from app.modules.usuarios.models import UsuarioPublic
from app.modules.ingredientes.schemas import (
    IngredienteCreate, IngredientePublic, IngredienteUpdate, IngredienteList,
)
from app.modules.ingredientes.service import IngredienteService

router = APIRouter()


def get_service(session: Annotated[Session, Depends(get_session)]) -> IngredienteService:
    return IngredienteService(session)


@router.post("/", response_model=IngredientePublic, status_code=status.HTTP_201_CREATED)
def create_ingrediente(
    data: IngredienteCreate,
    svc: Annotated[IngredienteService, Depends(get_service)],
    _admin: Annotated[UsuarioPublic, Depends(require_role(["ADMIN"]))],
):
    return svc.create(data)


@router.get("/", response_model=IngredienteList)
def list_ingredientes(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    svc: IngredienteService = Depends(get_service),
    _user: UsuarioPublic = Depends(get_current_active_user),
):
    return svc.get_all(offset=offset, limit=limit)


@router.get("/{ingrediente_id}", response_model=IngredientePublic)
def get_ingrediente(
    ingrediente_id: int,
    svc: IngredienteService = Depends(get_service),
    _user: UsuarioPublic = Depends(get_current_active_user),
):
    return svc.get_by_id(ingrediente_id)


@router.patch("/{ingrediente_id}", response_model=IngredientePublic)
def update_ingrediente(
    ingrediente_id: int,
    data: IngredienteUpdate,
    svc: IngredienteService = Depends(get_service),
    _admin: UsuarioPublic = Depends(require_role(["ADMIN"])),
):
    return svc.update(ingrediente_id, data)


@router.put("/{ingrediente_id}", response_model=IngredientePublic)
def replace_ingrediente(
    ingrediente_id: int,
    data: IngredienteUpdate,
    svc: IngredienteService = Depends(get_service),
    _admin: UsuarioPublic = Depends(require_role(["ADMIN"])),
):
    return svc.update(ingrediente_id, data)


@router.delete("/{ingrediente_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingrediente(
    ingrediente_id: int,
    svc: IngredienteService = Depends(get_service),
    _admin: UsuarioPublic = Depends(require_role(["ADMIN"])),
):
    svc.delete(ingrediente_id)
