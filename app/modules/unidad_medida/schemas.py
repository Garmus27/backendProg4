from typing import Optional, List
from sqlmodel import SQLModel, Field


class UnidadMedidaCreate(SQLModel):
    nombre: str = Field(max_length=50)
    simbolo: str = Field(max_length=10)
    tipo: str = Field(max_length=20)


class UnidadMedidaUpdate(SQLModel):
    nombre: Optional[str] = Field(default=None, max_length=50)
    simbolo: Optional[str] = Field(default=None, max_length=10)
    tipo: Optional[str] = Field(default=None, max_length=20)


class UnidadMedidaPublic(SQLModel):
    id: int
    nombre: str
    simbolo: str
    tipo: str


class UnidadMedidaList(SQLModel):
    data: List[UnidadMedidaPublic]
    total: int
