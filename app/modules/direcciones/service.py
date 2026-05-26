from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlmodel import Session

from app.modules.direcciones.models import DireccionEntrega
from app.modules.direcciones.schemas import (
    DireccionCreate, DireccionPublic, DireccionUpdate, DireccionList,
)
from app.modules.direcciones.unit_of_work import DireccionUnitOfWork


class DireccionService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _get_or_404(self, uow, direccion_id: int, usuario_id: int) -> DireccionEntrega:
        d = uow.direcciones.get_by_id(direccion_id)
        if not d or d.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Dirección id={direccion_id} no encontrada")
        if d.usuario_id != usuario_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="No tenés permisos sobre esta dirección")
        return d

    def _desmarcar_principal(self, uow, usuario_id: int) -> None:
        """Si hay una dirección principal activa, la desmarca."""
        principal = uow.direcciones.get_principal(usuario_id)
        if principal:
            principal.es_principal = False
            uow.direcciones.add(principal)

    def create(self, data: DireccionCreate, usuario_id: int) -> DireccionPublic:
        with DireccionUnitOfWork(self._session) as uow:
            if data.es_principal:
                self._desmarcar_principal(uow, usuario_id)
            d = DireccionEntrega(
                usuario_id=usuario_id,
                alias=data.alias,
                linea1=data.linea1,
                linea2=data.linea2,
                ciudad=data.ciudad,
                provincia=data.provincia,
                codigo_postal=data.codigo_postal,
                latitud=data.latitud,
                longitud=data.longitud,
                es_principal=data.es_principal,
            )
            uow.direcciones.add(d)
            result = DireccionPublic.model_validate(d)
        return result

    def list_mis_direcciones(self, usuario_id: int) -> DireccionList:
        with DireccionUnitOfWork(self._session) as uow:
            dirs = uow.direcciones.get_by_usuario(usuario_id)
            total = uow.direcciones.count_by_usuario(usuario_id)
        return DireccionList(
            data=[DireccionPublic.model_validate(d) for d in dirs],
            total=total,
        )

    def get_by_id(self, direccion_id: int, usuario_id: int) -> DireccionPublic:
        with DireccionUnitOfWork(self._session) as uow:
            d = self._get_or_404(uow, direccion_id, usuario_id)
            result = DireccionPublic.model_validate(d)
        return result

    def update(self, direccion_id: int, data: DireccionUpdate, usuario_id: int) -> DireccionPublic:
        with DireccionUnitOfWork(self._session) as uow:
            d = self._get_or_404(uow, direccion_id, usuario_id)
            if data.es_principal is True and not d.es_principal:
                self._desmarcar_principal(uow, usuario_id)
            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(d, field, value)
            d.updated_at = datetime.now(timezone.utc)
            uow.direcciones.add(d)
            result = DireccionPublic.model_validate(d)
        return result

    def delete(self, direccion_id: int, usuario_id: int) -> None:
        with DireccionUnitOfWork(self._session) as uow:
            d = self._get_or_404(uow, direccion_id, usuario_id)
            d.deleted_at = datetime.now(timezone.utc)
            uow.direcciones.add(d)
