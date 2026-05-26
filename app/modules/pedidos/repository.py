from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.core.repository import BaseRepository
from app.modules.pedidos.models import (
    Pedido, DetallePedido, HistorialEstadoPedido,
    EstadoPedido, FormaPago, Pago,
)


class PedidoRepository(BaseRepository[Pedido]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Pedido)

    def get_by_usuario(self, usuario_id: int, offset: int = 0, limit: int = 20) -> list[Pedido]:
        return list(self.session.exec(
            select(Pedido)
            .where(Pedido.usuario_id == usuario_id)
            .where(Pedido.deleted_at == None)
            .offset(offset).limit(limit)
        ).all())

    def get_by_id_con_detalle(self, pedido_id: int) -> Pedido | None:
        return self.session.get(Pedido, pedido_id)

    def count_by_usuario(self, usuario_id: int) -> int:
        return len(self.session.exec(
            select(Pedido)
            .where(Pedido.usuario_id == usuario_id)
            .where(Pedido.deleted_at == None)
        ).all())

    def count(self) -> int:
        return len(self.session.exec(
            select(Pedido).where(Pedido.deleted_at == None)
        ).all())


class DetallePedidoRepository(BaseRepository[DetallePedido]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, DetallePedido)

    def get_by_pedido(self, pedido_id: int) -> list[DetallePedido]:
        return list(self.session.exec(
            select(DetallePedido).where(DetallePedido.pedido_id == pedido_id)
        ).all())

    def get_by_ids(self, pedido_id: int, producto_id: int) -> DetallePedido | None:
        return self.session.exec(
            select(DetallePedido)
            .where(DetallePedido.pedido_id == pedido_id)
            .where(DetallePedido.producto_id == producto_id)
        ).first()


class HistorialEstadoRepository(BaseRepository[HistorialEstadoPedido]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, HistorialEstadoPedido)

    def get_by_pedido(self, pedido_id: int) -> list[HistorialEstadoPedido]:
        return list(self.session.exec(
            select(HistorialEstadoPedido)
            .where(HistorialEstadoPedido.pedido_id == pedido_id)
            .order_by(HistorialEstadoPedido.created_at)
        ).all())


class EstadoPedidoRepository(BaseRepository[EstadoPedido]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, EstadoPedido)

    def get_by_codigo(self, codigo: str) -> EstadoPedido | None:
        return self.session.get(EstadoPedido, codigo)

    def get_all_estados(self) -> list[EstadoPedido]:
        return list(self.session.exec(
            select(EstadoPedido).order_by(EstadoPedido.orden)
        ).all())


class FormaPagoRepository(BaseRepository[FormaPago]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, FormaPago)

    def get_by_codigo(self, codigo: str) -> FormaPago | None:
        return self.session.get(FormaPago, codigo)

    def get_habilitadas(self) -> list[FormaPago]:
        return list(self.session.exec(
            select(FormaPago).where(FormaPago.habilitado == True)
        ).all())


class PagoRepository(BaseRepository[Pago]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Pago)

    def get_by_pedido(self, pedido_id: int) -> list[Pago]:
        return list(self.session.exec(
            select(Pago).where(Pago.pedido_id == pedido_id)
        ).all())

    def get_by_idempotency_key(self, key: str) -> Pago | None:
        return self.session.exec(
            select(Pago).where(Pago.idempotency_key == key)
        ).first()
