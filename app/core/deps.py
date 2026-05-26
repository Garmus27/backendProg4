from datetime import datetime, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from app.core.security import decode_access_token
from app.core.database import get_session
from app.modules.usuarios.models import Usuario, UsuarioPublic, UsuarioRol


# sobreescribimos OAuth2PasswordBearer para que lea el token de la cookie
# en lugar del header Authorization, así JavaScript nunca puede leerlo
class OAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> str | None:
        token = request.cookies.get("access_token")
        if not token:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No autenticado",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None
        return token


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/auth/token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_session)],
) -> UsuarioPublic:
    # decodificamos el token y buscamos el usuario en la DB
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    username: str | None = payload.get("sub")
    if username is None:
        raise credentials_exception

    user = session.exec(select(Usuario).where(Usuario.username == username)).first()
    if user is None:
        raise credentials_exception

    # cargamos los roles activos del usuario desde la DB
    # filtramos los que expiraron
    now = datetime.now(timezone.utc)
    registros = session.exec(
        select(UsuarioRol)
        .where(UsuarioRol.usuario_id == user.id)
        .where(
            (UsuarioRol.expires_at == None) |
            (UsuarioRol.expires_at > now)
        )
    ).all()
    roles = [r.rol_codigo for r in registros]

    return UsuarioPublic(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        disabled=user.disabled,
        roles=roles,
    )


async def get_current_active_user(
    current_user: Annotated[UsuarioPublic, Depends(get_current_user)],
) -> UsuarioPublic:
    # si el usuario está desactivado lo bloqueamos acá
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cuenta de usuario desactivada",
        )
    return current_user


def require_role(allowed_roles: list[str]):
    # factory que genera una dependencia para proteger endpoints por rol
    # usamos any() porque un usuario puede tener múltiples roles
    async def role_checker(
        current_user: Annotated[UsuarioPublic, Depends(get_current_active_user)],
    ) -> UsuarioPublic:
        if not any(r in allowed_roles for r in current_user.roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Permisos insuficientes. Tus roles son {current_user.roles}. "
                    f"Se requiere uno de: {allowed_roles}"
                ),
            )
        return current_user
    return role_checker
