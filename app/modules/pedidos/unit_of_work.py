from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.pedidos.repository import (
    PedidoRepository, DetallePedidoRepository, HistorialEstadoRepository,
    EstadoPedidoRepository, FormaPagoRepository, PagoRepository,
)
from app.modules.productos.repository import ProductoRepository, ProductoIngredienteRepository
from app.modules.ingredientes.repository import IngredienteRepository


class PedidoUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.pedidos = PedidoRepository(session)
        self.detalles = DetallePedidoRepository(session)
        self.historial = HistorialEstadoRepository(session)
        self.estados = EstadoPedidoRepository(session)
        self.formas_pago = FormaPagoRepository(session)
        self.pagos = PagoRepository(session)
        self.productos = ProductoRepository(session)
        # necesitamos el repo de ingredientes para descontar su stock al crear pedidos
        self.producto_ingredientes = ProductoIngredienteRepository(session)
        self.ingredientes = IngredienteRepository(session)
