from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field


class CategoriaCreate(SQLModel):
    nombre: str = Field(max_length=100)
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    parent_id: Optional[int] = None


class CategoriaUpdate(SQLModel):
    nombre: Optional[str] = Field(default=None, max_length=100)
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    parent_id: Optional[int] = None


class CategoriaPublic(SQLModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    parent_id: Optional[int] = None
    created_at: datetime


class CategoriaList(SQLModel):
    data: List[CategoriaPublic]
    total: int
