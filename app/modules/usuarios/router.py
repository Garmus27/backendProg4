from typing import Annotated
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.core.config import settings
from app.core.database import get_session
from app.core.deps import get_current_active_user, require_role
from app.modules.usuarios.models import (
    UsuarioCreate, UsuarioPublic, Token, RolPublic, AsignarRolRequest,
)
from app.modules.usuarios.service import UsuarioService

router = APIRouter()


def get_service(session: Annotated[Session, Depends(get_session)]) -> UsuarioService:
    return UsuarioService(session)


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )


@router.post("/register", response_model=UsuarioPublic, status_code=status.HTTP_201_CREATED)
def register(
    data: UsuarioCreate,
    svc: Annotated[UsuarioService, Depends(get_service)],
):
    return svc.register(data)


@router.post("/token", response_model=Token)
def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    svc: Annotated[UsuarioService, Depends(get_service)],
):
    token, raw_refresh, access_token = svc.authenticate(form_data.username, form_data.password)
    set_auth_cookies(response, access_token, raw_refresh)
    return token


@router.post("/refresh", response_model=Token)
def refresh(
    response: Response,
    svc: Annotated[UsuarioService, Depends(get_service)],
    refresh_token: Annotated[str | None, Cookie()] = None,
):
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Refresh token no encontrado")
    token, new_raw_refresh, access_token = svc.refresh(refresh_token)
    set_auth_cookies(response, access_token, new_raw_refresh)
    return token


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    svc: Annotated[UsuarioService, Depends(get_service)],
    _user: Annotated[UsuarioPublic, Depends(get_current_active_user)],
    refresh_token: Annotated[str | None, Cookie()] = None,
):
    svc.logout(refresh_token, _user.id)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")


@router.get("/me", response_model=UsuarioPublic)
def read_me(
    current_user: Annotated[UsuarioPublic, Depends(get_current_active_user)],
):
    return current_user


# ── Roles ──────────────────────────────────────────────────────────────────────

@router.get("/roles", response_model=list[RolPublic])
def list_roles(
    _user: Annotated[UsuarioPublic, Depends(get_current_active_user)],
    svc: Annotated[UsuarioService, Depends(get_service)],
):
    return svc.list_roles()


@router.post("/admin/usuarios/{usuario_id}/roles", response_model=UsuarioPublic)
def asignar_rol(
    usuario_id: int,
    data: AsignarRolRequest,
    admin: Annotated[UsuarioPublic, Depends(require_role(["ADMIN"]))],
    svc: Annotated[UsuarioService, Depends(get_service)],
):
    return svc.asignar_rol(usuario_id, data, asignado_por_id=admin.id)


@router.delete("/admin/usuarios/{usuario_id}/roles/{rol_codigo}",
               response_model=UsuarioPublic)
def quitar_rol(
    usuario_id: int,
    rol_codigo: str,
    _admin: Annotated[UsuarioPublic, Depends(require_role(["ADMIN"]))],
    svc: Annotated[UsuarioService, Depends(get_service)],
):
    return svc.quitar_rol(usuario_id, rol_codigo)


# ── Administración de usuarios ─────────────────────────────────────────────────

@router.get("/admin/usuarios", response_model=list[UsuarioPublic])
def list_users(
    _admin: Annotated[UsuarioPublic, Depends(require_role(["ADMIN"]))],
    svc: Annotated[UsuarioService, Depends(get_service)],
):
    return svc.list_all()


@router.post("/admin/usuarios/{user_id}/desactivar", response_model=UsuarioPublic)
def deactivate_user(
    user_id: int,
    _admin: Annotated[UsuarioPublic, Depends(require_role(["ADMIN"]))],
    svc: Annotated[UsuarioService, Depends(get_service)],
):
    return svc.set_disabled(user_id, disabled=True)


@router.post("/admin/usuarios/{user_id}/activar", response_model=UsuarioPublic)
def activate_user(
    user_id: int,
    _admin: Annotated[UsuarioPublic, Depends(require_role(["ADMIN"]))],
    svc: Annotated[UsuarioService, Depends(get_service)],
):
    return svc.set_disabled(user_id, disabled=False)
