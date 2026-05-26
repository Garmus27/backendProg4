from fastapi import HTTPException, status
from sqlmodel import Session

from app.modules.unidad_medida.models import UnidadMedida
from app.modules.unidad_medida.schemas import (
    UnidadMedidaCreate, UnidadMedidaPublic, UnidadMedidaUpdate, UnidadMedidaList,
)
from app.modules.unidad_medida.unit_of_work import UnidadMedidaUnitOfWork


class UnidadMedidaService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _get_or_404(self, uow, unidad_id: int) -> UnidadMedida:
        u = uow.unidades.get_by_id(unidad_id)
        if not u:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"UnidadMedida id={unidad_id} no encontrada")
        return u

    def _assert_nombre_unico(self, uow, nombre: str) -> None:
        if uow.unidades.get_by_nombre(nombre):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"Ya existe una unidad con el nombre '{nombre}'")

    def _assert_simbolo_unico(self, uow, simbolo: str) -> None:
        if uow.unidades.get_by_simbolo(simbolo):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"Ya existe una unidad con el símbolo '{simbolo}'")

    def create(self, data: UnidadMedidaCreate) -> UnidadMedidaPublic:
        with UnidadMedidaUnitOfWork(self._session) as uow:
            self._assert_nombre_unico(uow, data.nombre)
            self._assert_simbolo_unico(uow, data.simbolo)
            u = UnidadMedida.model_validate(data)
            uow.unidades.add(u)
            result = UnidadMedidaPublic.model_validate(u)
        return result

    def get_all(self, offset: int = 0, limit: int = 20) -> UnidadMedidaList:
        with UnidadMedidaUnitOfWork(self._session) as uow:
            unidades = uow.unidades.get_all(offset=offset, limit=limit)
            total = uow.unidades.count()
            result = UnidadMedidaList(
                data=[UnidadMedidaPublic.model_validate(u) for u in unidades],
                total=total,
            )
        return result

    def get_by_id(self, unidad_id: int) -> UnidadMedidaPublic:
        with UnidadMedidaUnitOfWork(self._session) as uow:
            u = self._get_or_404(uow, unidad_id)
            result = UnidadMedidaPublic.model_validate(u)
        return result

    def update(self, unidad_id: int, data: UnidadMedidaUpdate) -> UnidadMedidaPublic:
        with UnidadMedidaUnitOfWork(self._session) as uow:
            u = self._get_or_404(uow, unidad_id)
            if data.nombre and data.nombre != u.nombre:
                self._assert_nombre_unico(uow, data.nombre)
            if data.simbolo and data.simbolo != u.simbolo:
                self._assert_simbolo_unico(uow, data.simbolo)
            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(u, field, value)
            uow.unidades.add(u)
            result = UnidadMedidaPublic.model_validate(u)
        return result

    def delete(self, unidad_id: int) -> None:
        with UnidadMedidaUnitOfWork(self._session) as uow:
            u = self._get_or_404(uow, unidad_id)
            uow.unidades.delete(u)
