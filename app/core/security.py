from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# configuramos bcrypt con rounds=12, que es lo que recomienda la cátedra
# más rounds = más lento = más difícil de atacar por fuerza bruta
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)


def hash_password(plain: str) -> str:
    # convierte la contraseña en texto plano a un hash bcrypt
    # bcrypt agrega salt automáticamente, así que dos hashes del mismo texto son distintos
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    # compara la contraseña plana con el hash guardado en la DB
    # la comparación es timing-attack safe, siempre tarda lo mismo
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    # generamos el JWT de acceso, firmado con la SECRET_KEY
    # copiamos el payload para no mutar el dict original
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    # agregamos el tipo y la expiración al payload
    to_encode.update({"type": "access", "exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    # igual que el access token pero con más tiempo de vida
    # lo diferenciamos con type=refresh para que no se pueda usar como access
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"type": "refresh", "exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    # intentamos decodificar el JWT, si falla por cualquier motivo devolvemos None
    # jose valida la firma y la expiración automáticamente
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


def decode_refresh_token(token: str) -> dict | None:
    # lo mismo pero validando que sea un refresh token y no un access token
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None
