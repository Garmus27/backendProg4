from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.usuarios.repository import (
    UsuarioRepository, RolRepository,
    UsuarioRolRepository, RefreshTokenRepository,
)


class UsuarioUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.usuarios = UsuarioRepository(session)
        self.roles = RolRepository(session)
        self.usuario_roles = UsuarioRolRepository(session)
        self.refresh_tokens = RefreshTokenRepository(session)
