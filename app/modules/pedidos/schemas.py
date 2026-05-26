from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlmodel import SQLModel, Field


class ItemPedidoRequest(SQLModel):
    producto_id: int
    cantidad: int = Field(ge=1)
    personalizacion: Optional[List[int]] = None


class PedidoCreate(SQLModel):
    forma_pago_codigo: str
    direccion_id: Optional[int] = None
    notas: Optional[str] = None
    items: List[ItemPedidoRequest] = Field(min_length=1)


class AvanzarEstadoRequest(SQLModel):
    estado_hacia: str
    motivo: Optional[str] = None


class PedidoUpdate(SQLModel):
    estado_hacia: Optional[str] = None
    motivo: Optional[str] = None
    notas: Optional[str] = None


class DetallePedidoPublic(SQLModel):
    producto_id: int
    cantidad: int
    nombre_snapshot: str
    precio_snapshot: Decimal
    subtotal_snap: Decimal
    personalizacion: Optional[List[int]] = None


class HistorialEstadoPublic(SQLModel):
    id: int
    estado_desde: Optional[str]
    estado_hacia: str
    usuario_id: Optional[int]
    motivo: Optional[str]
    created_at: datetime


class PedidoPublic(SQLModel):
    id: int
    usuario_id: int
    direccion_id: Optional[int]
    estado_codigo: str
    forma_pago_codigo: str
    subtotal: Decimal
    descuento: Decimal
    costo_envio: Decimal
    total: Decimal
    notas: Optional[str]
    created_at: datetime


class PedidoConDetalle(SQLModel):
    id: int
    usuario_id: int
    direccion_id: Optional[int]
    estado_codigo: str
    forma_pago_codigo: str
    subtotal: Decimal
    descuento: Decimal
    costo_envio: Decimal
    total: Decimal
    notas: Optional[str]
    created_at: datetime
    items: List[DetallePedidoPublic] = []
    historial: List[HistorialEstadoPublic] = []


class PedidoList(SQLModel):
    data: List[PedidoPublic]
    total: int


class EstadoPedidoPublic(SQLModel):
    codigo: str
    descripcion: str
    orden: int
    es_terminal: bool


class FormaPagoPublic(SQLModel):
    codigo: str
    descripcion: str
    habilitado: bool
