from pydantic import computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # datos de conexión a PostgreSQL
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "parcial_db"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        # construimos la URL de conexión a partir de las variables individuales
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # configuración JWT
    SECRET_KEY: str  # obligatorio, no tiene default, falla al arrancar si no está
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
