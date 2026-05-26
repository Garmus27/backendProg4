from sqlmodel import Session, select
from app.core.database import engine
from app.core.security import hash_password
from app.modules.usuarios.models import Rol, Usuario, UsuarioRol
from app.modules.unidad_medida.models import UnidadMedida
from app.modules.pedidos.models import EstadoPedido, FormaPago

# roles del sistema según el UML
ROLES_SEED = [
    Rol(codigo="ADMIN",   nombre="Administrador",  descripcion="Acceso total sin restricciones"),
    Rol(codigo="STOCK",   nombre="Stock",           descripcion="Actualiza stock y disponibilidad"),
    Rol(codigo="PEDIDOS", nombre="Pedidos",         descripcion="Avanza estados confirmado → entregado"),
    Rol(codigo="CLIENT",  nombre="Cliente",         descripcion="Opera solo sus propios datos"),
]

# unidades de medida del catálogo inicial
UNIDADES_SEED = [
    UnidadMedida(nombre="kilogramo",      simbolo="kg",  tipo="masa"),
    UnidadMedida(nombre="gramo",          simbolo="g",   tipo="masa"),
    UnidadMedida(nombre="litro",          simbolo="L",   tipo="volumen"),
    UnidadMedida(nombre="mililitro",      simbolo="mL",  tipo="volumen"),
    UnidadMedida(nombre="pieza",          simbolo="u",   tipo="unidad"),
    UnidadMedida(nombre="docena",         simbolo="doc", tipo="unidad"),
    UnidadMedida(nombre="metro cuadrado", simbolo="m²",  tipo="área"),
]

# estados del pedido con su orden en la FSM
ESTADOS_SEED = [
    EstadoPedido(codigo="pendiente",      descripcion="Pendiente de confirmación", orden=1, es_terminal=False),
    EstadoPedido(codigo="confirmado",     descripcion="Confirmado",               orden=2, es_terminal=False),
    EstadoPedido(codigo="en_preparacion", descripcion="En preparación",           orden=3, es_terminal=False),
    EstadoPedido(codigo="en_camino",      descripcion="En camino",                orden=4, es_terminal=False),
    EstadoPedido(codigo="entregado",      descripcion="Entregado",                orden=5, es_terminal=True),
    EstadoPedido(codigo="cancelado",      descripcion="Cancelado",                orden=6, es_terminal=True),
]

# formas de pago disponibles
FORMAS_PAGO_SEED = [
    FormaPago(codigo="EFECTIVO",      descripcion="Retiro en local",        habilitado=True),
    FormaPago(codigo="TRANSFERENCIA", descripcion="Transferencia bancaria", habilitado=True),
]


def run_seed() -> None:
    with Session(engine) as session:
        for rol in ROLES_SEED:
            if not session.get(Rol, rol.codigo):
                session.add(rol)

        # para las unidades chequeamos por símbolo para evitar duplicados
        existentes_u = {u.simbolo for u in session.exec(select(UnidadMedida)).all()}
        for unidad in UNIDADES_SEED:
            if unidad.simbolo not in existentes_u:
                session.add(unidad)

        for estado in ESTADOS_SEED:
            if not session.get(EstadoPedido, estado.codigo):
                session.add(estado)

        for forma in FORMAS_PAGO_SEED:
            if not session.get(FormaPago, forma.codigo):
                session.add(forma)

        # creamos el usuario admin si no existe
        admin = session.exec(select(Usuario).where(Usuario.username == "admin")).first()
        if not admin:
            admin = Usuario(
                username="admin",
                full_name="Administrador",
                email="admin@admin.com",
                hashed_password=hash_password("admin1234"),
            )
            session.add(admin)
            session.flush()
            session.add(UsuarioRol(
                usuario_id=admin.id,
                rol_codigo="ADMIN",
            ))

        session.commit()
        print("Seed completado.")


if __name__ == "__main__":
    run_seed()