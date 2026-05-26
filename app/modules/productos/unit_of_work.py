from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.productos.repository import (
    ProductoRepository, ProductoCategoriaRepository, ProductoIngredienteRepository,
)
from app.modules.categorias.repository import CategoriaRepository
from app.modules.ingredientes.repository import IngredienteRepository
from app.modules.unidad_medida.repository import UnidadMedidaRepository


class ProductoUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.productos = ProductoRepository(session)
        self.producto_categorias = ProductoCategoriaRepository(session)
        self.producto_ingredientes = ProductoIngredienteRepository(session)
        self.categorias = CategoriaRepository(session)
        self.ingredientes = IngredienteRepository(session)
        self.unidades = UnidadMedidaRepository(session)
