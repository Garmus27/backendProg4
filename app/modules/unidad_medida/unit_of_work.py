from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.unidad_medida.repository import UnidadMedidaRepository


class UnidadMedidaUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.unidades = UnidadMedidaRepository(session)
