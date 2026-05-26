from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.core.deps import get_current_active_user, require_role
from app.modules.usuarios.models import UsuarioPublic
from app.modules.categorias.schemas import (
    CategoriaCreate, CategoriaPublic, CategoriaUpdate, CategoriaList,
)
from app.modules.categorias.service import CategoriaService

router = APIRouter()


def get_service(session: Annotated[Session, Depends(get_session)]) -> CategoriaService:
    return CategoriaService(session)


@router.post("/", response_model=CategoriaPublic, status_code=status.HTTP_201_CREATED)
def create_categoria(
    data: CategoriaCreate,
    svc: Annotated[CategoriaService, Depends(get_service)],
    _admin: Annotated[UsuarioPublic, Depends(require_role(["ADMIN"]))],
):
    return svc.create(data)


@router.get("/", response_model=CategoriaList)
def list_categorias(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    svc: CategoriaService = Depends(get_service),
    _user: UsuarioPublic = Depends(get_current_active_user),
):
    return svc.get_all(offset=offset, limit=limit)


@router.get("/{categoria_id}", response_model=CategoriaPublic)
def get_categoria(
    categoria_id: int,
    svc: CategoriaService = Depends(get_service),
    _user: UsuarioPublic = Depends(get_current_active_user),
):
    return svc.get_by_id(categoria_id)


@router.patch("/{categoria_id}", response_model=CategoriaPublic)
def update_categoria(
    categoria_id: int,
    data: CategoriaUpdate,
    svc: CategoriaService = Depends(get_service),
    _admin: UsuarioPublic = Depends(require_role(["ADMIN"])),
):
    return svc.update(categoria_id, data)


@router.put("/{categoria_id}", response_model=CategoriaPublic)
def replace_categoria(
    categoria_id: int,
    data: CategoriaUpdate,
    svc: CategoriaService = Depends(get_service),
    _admin: UsuarioPublic = Depends(require_role(["ADMIN"])),
):
    return svc.update(categoria_id, data)


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_categoria(
    categoria_id: int,
    svc: CategoriaService = Depends(get_service),
    _admin: UsuarioPublic = Depends(require_role(["ADMIN"])),
):
    svc.delete(categoria_id)
