from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.modules.categorias.models import Categoria
    from app.modules.ingredientes.models import Ingrediente


class ProductoCategoria(SQLModel, table=True):
    __tablename__ = "producto_categoria"

    # tabla puente para la relación N:N entre productos y categorías
    # un producto puede estar en varias categorías, pero solo una puede ser la principal
    producto_id: int = Field(foreign_key="productos.id", primary_key=True)
    categoria_id: int = Field(foreign_key="categorias.id", primary_key=True)
    es_principal: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    producto: Optional["Producto"] = Relationship(back_populates="producto_categorias")
    categoria: Optional["Categoria"] = Relationship(back_populates="producto_categorias")


class ProductoIngrediente(SQLModel, table=True):
    __tablename__ = "producto_ingrediente"

    # tabla puente para la relación N:N entre productos e ingredientes
    # guardamos la cantidad y la unidad de medida en esta tabla porque son datos de la relación
    producto_id: int = Field(foreign_key="productos.id", primary_key=True)
    ingrediente_id: int = Field(foreign_key="ingredientes.id", primary_key=True)
    cantidad: float = Field(gt=0)
    unidad_medida_id: int = Field(foreign_key="unidades_medida.id", nullable=False)
    es_removible: bool = Field(default=False, nullable=False)

    producto: Optional["Producto"] = Relationship(back_populates="producto_ingredientes")
    ingrediente: Optional["Ingrediente"] = Relationship(back_populates="producto_ingredientes")


class Producto(SQLModel, table=True):
    __tablename__ = "productos"

    id: Optional[int] = Field(default=None, primary_key=True)
    unidad_venta_id: Optional[int] = Field(default=None, foreign_key="unidades_medida.id")
    nombre: str = Field(max_length=150, nullable=False, index=True)
    descripcion: Optional[str] = Field(default=None)
    precio_base: float = Field(ge=0, nullable=False)
    stock_cantidad: int = Field(default=0, ge=0, nullable=False)
    disponible: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = Field(default=None)

    producto_categorias: List["ProductoCategoria"] = Relationship(back_populates="producto")
    producto_ingredientes: List["ProductoIngrediente"] = Relationship(back_populates="producto")
