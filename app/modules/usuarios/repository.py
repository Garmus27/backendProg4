from datetime import datetime, timezone
from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.usuarios.models import Usuario, RefreshToken, Rol, UsuarioRol


class UsuarioRepository(BaseRepository[Usuario]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Usuario)

    def get_by_username(self, username: str) -> Usuario | None:
        return self.session.exec(
            select(Usuario).where(Usuario.username == username)
        ).first()

    def get_by_email(self, email: str) -> Usuario | None:
        return self.session.exec(
            select(Usuario).where(Usuario.email == email)
        ).first()


class RolRepository(BaseRepository[Rol]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Rol)

    def get_by_codigo(self, codigo: str) -> Rol | None:
        return self.session.get(Rol, codigo)

    def get_all_roles(self) -> list[Rol]:
        return list(self.session.exec(select(Rol)).all())


class UsuarioRolRepository(BaseRepository[UsuarioRol]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, UsuarioRol)

    def get_roles_de_usuario(self, usuario_id: int) -> list[str]:
        now = datetime.now(timezone.utc)
        registros = self.session.exec(
            select(UsuarioRol)
            .where(UsuarioRol.usuario_id == usuario_id)
            .where(
                (UsuarioRol.expires_at == None) |
                (UsuarioRol.expires_at > now)
            )
        ).all()
        return [r.rol_codigo for r in registros]

    def get_asignacion(self, usuario_id: int, rol_codigo: str) -> UsuarioRol | None:
        return self.session.exec(
            select(UsuarioRol)
            .where(UsuarioRol.usuario_id == usuario_id)
            .where(UsuarioRol.rol_codigo == rol_codigo)
        ).first()

    def remove_asignacion(self, asignacion: UsuarioRol) -> None:
        self.session.delete(asignacion)
        self.session.flush()


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, RefreshToken)

    def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        return self.session.exec(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        ).first()

    def revoke(self, refresh_token: RefreshToken) -> None:
        refresh_token.revoked_at = datetime.now(timezone.utc)
        self.session.add(refresh_token)
        self.session.flush()

    def revoke_all_for_user(self, usuario_id: int) -> None:
        tokens = self.session.exec(
            select(RefreshToken)
            .where(RefreshToken.usuario_id == usuario_id)
            .where(RefreshToken.revoked_at == None)
        ).all()
        now = datetime.now(timezone.utc)
        for token in tokens:
            token.revoked_at = now
            self.session.add(token)
        self.session.flush()

    def delete_expired(self) -> None:
        expired = self.session.exec(
            select(RefreshToken)
            .where(RefreshToken.expires_at < datetime.now(timezone.utc))
        ).all()
        for token in expired:
            self.session.delete(token)
        self.session.flush()
