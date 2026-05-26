from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import ARRAY, Integer


class EstadoPedido(SQLModel, table=True):
    __tablename__ = "estados_pedido"

    codigo: str = Field(max_length=20, primary_key=True)
    descripcion: str = Field(max_length=80, nullable=False)
    orden: int = Field(nullable=False)
    es_terminal: bool = Field(nullable=False)


class FormaPago(SQLModel, table=True):
    __tablename__ = "formas_pago"

    codigo: str = Field(max_length=20, primary_key=True)
    descripcion: str = Field(max_length=80, nullable=False)
    habilitado: bool = Field(default=True, nullable=False)


class Pedido(SQLModel, table=True):
    __tablename__ = "pedidos"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuarios.id", nullable=False)
    direccion_id: Optional[int] = Field(default=None, foreign_key="direcciones_entrega.id")
    estado_codigo: str = Field(foreign_key="estados_pedido.codigo", nullable=False)
    forma_pago_codigo: str = Field(foreign_key="formas_pago.codigo", nullable=False)

    subtotal: Decimal = Field(nullable=False, decimal_places=2, max_digits=10)
    descuento: Decimal = Field(default=Decimal("0.00"), nullable=False, decimal_places=2, max_digits=10)
    costo_envio: Decimal = Field(default=Decimal("50.00"), nullable=False, decimal_places=2, max_digits=10)
    total: Decimal = Field(nullable=False, decimal_places=2, max_digits=10)
    notas: Optional[str] = Field(default=None)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = Field(default=None)


class DetallePedido(SQLModel, table=True):
    __tablename__ = "detalle_pedido"

    pedido_id: int = Field(foreign_key="pedidos.id", primary_key=True)
    producto_id: int = Field(foreign_key="productos.id", primary_key=True)
    cantidad: int = Field(ge=1, nullable=False)

    nombre_snapshot: str = Field(max_length=200, nullable=False)
    precio_snapshot: Decimal = Field(nullable=False, decimal_places=2, max_digits=10)
    subtotal_snap: Decimal = Field(nullable=False, decimal_places=2, max_digits=10)

    personalizacion: Optional[List[int]] = Field(
        default=None,
        sa_column=Column(ARRAY(Integer), nullable=True)
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HistorialEstadoPedido(SQLModel, table=True):
    __tablename__ = "historial_estado_pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id", nullable=False)
    estado_desde: Optional[str] = Field(default=None, foreign_key="estados_pedido.codigo")
    estado_hacia: str = Field(foreign_key="estados_pedido.codigo", nullable=False)
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuarios.id")
    motivo: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Pago(SQLModel, table=True):
    __tablename__ = "pagos"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id", nullable=False)

    mp_payment_id: Optional[int] = Field(default=None, unique=True)
    mp_status: str = Field(max_length=30, nullable=False)
    mp_status_detail: Optional[str] = Field(default=None, max_length=100)
    external_reference: str = Field(max_length=100, unique=True, nullable=False)
    idempotency_key: str = Field(max_length=100, unique=True, nullable=False)
    transaction_amount: Decimal = Field(nullable=False, decimal_places=2, max_digits=10)
    payment_method_id: Optional[str] = Field(default=None, max_length=50)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
