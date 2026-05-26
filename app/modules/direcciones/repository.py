from datetime import datetime, timezone
from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.direcciones.models import DireccionEntrega


class DireccionRepository(BaseRepository[DireccionEntrega]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, DireccionEntrega)

    def get_by_usuario(self, usuario_id: int) -> list[DireccionEntrega]:
        return list(self.session.exec(
            select(DireccionEntrega)
            .where(DireccionEntrega.usuario_id == usuario_id)
            .where(DireccionEntrega.deleted_at == None)
        ).all())

    def get_principal(self, usuario_id: int) -> DireccionEntrega | None:
        return self.session.exec(
            select(DireccionEntrega)
            .where(DireccionEntrega.usuario_id == usuario_id)
            .where(DireccionEntrega.es_principal == True)
            .where(DireccionEntrega.deleted_at == None)
        ).first()

    def count_by_usuario(self, usuario_id: int) -> int:
        return len(self.session.exec(
            select(DireccionEntrega)
            .where(DireccionEntrega.usuario_id == usuario_id)
            .where(DireccionEntrega.deleted_at == None)
        ).all())
