from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.core.deps import get_current_active_user, require_role
from app.modules.usuarios.models import UsuarioPublic
from app.modules.productos.schemas import (
    ProductoCreate, ProductoPublic, ProductoUpdate, ProductoList,
    ProductoConDetalle, ProductoCategoriaCreate, ProductoIngredienteCreate,
)
from app.modules.productos.service import ProductoService

router = APIRouter()


def get_service(session: Annotated[Session, Depends(get_session)]) -> ProductoService:
    return ProductoService(session)


@router.post("/", response_model=ProductoPublic, status_code=status.HTTP_201_CREATED)
def create_producto(
    data: ProductoCreate,
    svc: Annotated[ProductoService, Depends(get_service)],
    _admin: Annotated[UsuarioPublic, Depends(require_role(["ADMIN"]))],
):
    return svc.create(data)


@router.get("/", response_model=ProductoList)
def list_productos(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    svc: ProductoService = Depends(get_service),
    _user: UsuarioPublic = Depends(get_current_active_user),
):
    return svc.get_all(offset=offset, limit=limit)


@router.get("/{producto_id}", response_model=ProductoConDetalle)
def get_producto(
    producto_id: int,
    svc: ProductoService = Depends(get_service),
    _user: UsuarioPublic = Depends(get_current_active_user),
):
    return svc.get_by_id(producto_id)


@router.patch("/{producto_id}", response_model=ProductoPublic)
def update_producto(
    producto_id: int,
    data: ProductoUpdate,
    svc: ProductoService = Depends(get_service),
    _admin: UsuarioPublic = Depends(require_role(["ADMIN", "STOCK"])),
):
    return svc.update(producto_id, data)


@router.put("/{producto_id}", response_model=ProductoPublic)
def replace_producto(
    producto_id: int,
    data: ProductoUpdate,
    svc: ProductoService = Depends(get_service),
    _admin: UsuarioPublic = Depends(require_role(["ADMIN", "STOCK"])),
):
    return svc.update(producto_id, data)


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_producto(
    producto_id: int,
    svc: ProductoService = Depends(get_service),
    _admin: UsuarioPublic = Depends(require_role(["ADMIN"])),
):
    svc.delete(producto_id)


@router.post("/{producto_id}/categorias", response_model=ProductoConDetalle)
def agregar_categoria(
    producto_id: int,
    data: ProductoCategoriaCreate,
    svc: ProductoService = Depends(get_service),
    _admin: UsuarioPublic = Depends(require_role(["ADMIN"])),
):
    return svc.agregar_categoria(producto_id, data)


@router.delete("/{producto_id}/categorias/{categoria_id}", response_model=ProductoConDetalle)
def quitar_categoria(
    producto_id: int,
    categoria_id: int,
    svc: ProductoService = Depends(get_service),
    _admin: UsuarioPublic = Depends(require_role(["ADMIN"])),
):
    return svc.quitar_categoria(producto_id, categoria_id)


@router.post("/{producto_id}/ingredientes", response_model=ProductoConDetalle)
def agregar_ingrediente(
    producto_id: int,
    data: ProductoIngredienteCreate,
    svc: ProductoService = Depends(get_service),
    _admin: UsuarioPublic = Depends(require_role(["ADMIN"])),
):
    return svc.agregar_ingrediente(producto_id, data)


@router.delete("/{producto_id}/ingredientes/{ingrediente_id}", response_model=ProductoConDetalle)
def quitar_ingrediente(
    producto_id: int,
    ingrediente_id: int,
    svc: ProductoService = Depends(get_service),
    _admin: UsuarioPublic = Depends(require_role(["ADMIN"])),
):
    return svc.quitar_ingrediente(producto_id, ingrediente_id)
