# PROYECTO BACKEND PROGRAMACION 4

## Integrantes

- Avellaneda Emmanuel
- Sabrina Moreira
- Matias Ferro
- Nicolas Llaneza
- David Lopez

## REPOSITORIO

https://github.com/Garmus27/backendProg4.git

## VIDEO MUESTRA DEL PROYECTO

https://drive.google.com/file/d/1A2tVmffUVA-cOdwUw3JkTmy5PJNwF-Gp/view?usp=sharing

---

API REST construida con FastAPI + SQLModel + PostgreSQL.

## Requisitos

- Docker y Docker Compose instalados
- O Python 3.12+ si preferís correrlo sin Docker

---

## Levantar con Docker (recomendado)

Desde la carpeta `backend/`:

    docker compose up --build

Esto levanta dos contenedores: la base de datos PostgreSQL y el backend FastAPI.
Las tablas se crean automáticamente y el seed carga los datos iniciales.

La API queda disponible en: http://localhost:8000  
Documentación interactiva: http://localhost:8000/docs

Para bajar los contenedores:

    docker compose down

Para bajar y borrar también los datos de la base:

    docker compose down -v

---

## Levantar sin Docker

### 1. Crear y activar el entorno virtual

Windows:

    python -m venv .venv
    .venv\Scripts\activate

Linux/Mac:

    python -m venv .venv
    source .venv/bin/activate

### 2. Instalar dependencias

    pip install -r requirements.txt

### 3. Configurar variables de entorno

Editá el archivo `.env` con tus datos de PostgreSQL:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=parcial_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

SECRET_KEY=tu_clave_secreta_larga
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

Para generar una `SECRET_KEY` segura:

    python -c "import secrets; print(secrets.token_hex(32))"

### 4. Crear la base de datos en PostgreSQL

```sql
CREATE DATABASE parcial_db;
```

### 5. Levantar el servidor

    uvicorn main:app --reload

---

## Estructura del proyecto

```
backend/
├── main.py                  # punto de entrada, registra routers
├── requirements.txt
├── .env
├── Dockerfile
├── docker-compose.yml
└── app/
    ├── core/                # infraestructura compartida
    │   ├── config.py        # variables de entorno con pydantic-settings
    │   ├── database.py      # engine y get_session
    │   ├── repository.py    # BaseRepository genérico
    │   ├── unit_of_work.py  # UoW base (commit/rollback)
    │   ├── security.py      # bcrypt + JWT
    │   └── deps.py          # dependencias de autenticación
    ├── db/
    │   └── seed.py          # datos iniciales (roles, unidades, estados, formas de pago)
    └── modules/
        ├── usuarios/        # auth, registro, roles RBAC
        ├── direcciones/     # direcciones de entrega por usuario
        ├── unidad_medida/   # catálogo de unidades
        ├── categorias/      # árbol de categorías
        ├── ingredientes/    # ingredientes con flag de alérgeno
        ├── productos/       # catálogo de productos
        └── pedidos/         # pedidos, FSM de estados, historial
```

## Datos que carga el seed automáticamente

**Roles:** `ADMIN`, `STOCK`, `PEDIDOS`, `CLIENT`

**Unidades de medida:** kg, g, L, mL, u, doc, m²

**Estados de pedido:** pendiente → confirmado → en_preparacion → en_camino → entregado / cancelado

**Formas de pago:** `EFECTIVO`, `TRANSFERENCIA`

---

## Flujo de autenticación

1. `POST /auth/register` — crear usuario (recibe rol `CLIENT` por defecto)
2. `POST /auth/token` — login con username y password, devuelve cookies HttpOnly
3. Todos los endpoints requieren estar autenticado
4. `POST /auth/refresh` — renueva el access token usando el refresh token
5. `POST /auth/logout` — cierra sesión y elimina las cookies

---

## Futuras actualizaciones

- implementar websockets para el seguimiento de los pedidos
- agregacion de forma de pago : MercadoPago
