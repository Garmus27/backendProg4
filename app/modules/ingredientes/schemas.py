from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field


class IngredienteCreate(SQLModel):
    nombre: str = Field(max_length=100)
    descripcion: Optional[str] = None
    es_alergeno: bool = False
    precio_por_unidad: float = Field(default=0.0, ge=0)
    stock_cantidad: float = Field(default=0.0, ge=0)


class IngredienteUpdate(SQLModel):
    nombre: Optional[str] = Field(default=None, max_length=100)
    descripcion: Optional[str] = None
    es_alergeno: Optional[bool] = None
    precio_por_unidad: Optional[float] = Field(default=None, ge=0)
    stock_cantidad: Optional[float] = Field(default=None, ge=0)


class IngredientePublic(SQLModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    es_alergeno: bool
    precio_por_unidad: float
    stock_cantidad: float
    created_at: datetime


class IngredienteList(SQLModel):
    data: List[IngredientePublic]
    total: int
