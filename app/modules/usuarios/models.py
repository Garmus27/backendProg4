import hashlib
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import EmailStr


class Rol(SQLModel, table=True):
    __tablename__ = "roles"

    # usamos el código como PK semántica para que sea legible en el JWT
    codigo: str = Field(max_length=20, primary_key=True)
    nombre: str = Field(max_length=50, unique=True, nullable=False)
    descripcion: Optional[str] = Field(default=None)


class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    full_name: str
    email: str = Field(unique=True, index=True)
    hashed_password: str
    disabled: bool = Field(default=False)


class UsuarioRol(SQLModel, table=True):
    __tablename__ = "usuario_roles"

    # PK compuesta: un usuario no puede tener el mismo rol dos veces
    usuario_id: int = Field(foreign_key="usuarios.id", primary_key=True)
    rol_codigo: str = Field(foreign_key="roles.codigo", primary_key=True, max_length=20)
    asignado_por_id: Optional[int] = Field(default=None, foreign_key="usuarios.id")
    expires_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuarios.id", nullable=False)
    # guardamos el hash del token, nunca el token en texto plano
    token_hash: str = Field(max_length=64, unique=True, nullable=False)
    expires_at: datetime = Field(nullable=False)
    revoked_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @staticmethod
    def hash_token(raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode()).hexdigest()

    def is_valid(self) -> bool:
        # el token es válido si no expiró y no fue revocado
        now = datetime.now(timezone.utc)
        expires = self.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return expires > now and self.revoked_at is None


class UsuarioCreate(SQLModel):
    username: str
    full_name: str
    email: EmailStr
    password: str = Field(min_length=8)


class UsuarioPublic(SQLModel):
    id: int
    username: str
    full_name: str
    email: str
    disabled: bool
    roles: list[str] = []


class Token(SQLModel):
    # el access_token viaja en la cookie, no en el body
    # acá solo devolvemos metadatos
    token_type: str = "bearer"
    expires_in: int


class RolPublic(SQLModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None


class AsignarRolRequest(SQLModel):
    rol_codigo: str
    expires_at: Optional[datetime] = None
