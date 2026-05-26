from datetime import datetime, timezone
from decimal import Decimal
from fastapi import HTTPException, status
from sqlmodel import Session

from app.modules.pedidos.models import (
    Pedido, DetallePedido, HistorialEstadoPedido,
)
from app.modules.pedidos.schemas import (
    PedidoCreate, PedidoPublic, PedidoConDetalle, PedidoList,
    DetallePedidoPublic, HistorialEstadoPublic,
    AvanzarEstadoRequest, EstadoPedidoPublic, FormaPagoPublic,
)
from app.modules.pedidos.unit_of_work import PedidoUnitOfWork

# mapa de transiciones válidas de la FSM
FSM: dict[str, list[str]] = {
    "pendiente":      ["confirmado", "cancelado"],
    "confirmado":     ["en_preparacion", "cancelado"],
    "en_preparacion": ["en_camino", "cancelado"],
    "en_camino":      ["entregado"],
    "entregado":      [],
    "cancelado":      [],
}

# cancelar desde en_preparacion requiere rol especial
CANCELACION_RESTRINGIDA = {"en_preparacion"}


class PedidoService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _get_or_404(self, uow, pedido_id: int) -> Pedido:
        p = uow.pedidos.get_by_id(pedido_id)
        if not p or p.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Pedido id={pedido_id} no encontrado")
        return p

    def _build_detalle(self, uow, pedido: Pedido) -> PedidoConDetalle:
        items = uow.detalles.get_by_pedido(pedido.id)
        historial = uow.historial.get_by_pedido(pedido.id)
        return PedidoConDetalle(
            id=pedido.id,
            usuario_id=pedido.usuario_id,
            direccion_id=pedido.direccion_id,
            estado_codigo=pedido.estado_codigo,
            forma_pago_codigo=pedido.forma_pago_codigo,
            subtotal=pedido.subtotal,
            descuento=pedido.descuento,
            costo_envio=pedido.costo_envio,
            total=pedido.total,
            notas=pedido.notas,
            created_at=pedido.created_at,
            items=[DetallePedidoPublic.model_validate(i) for i in items],
            historial=[HistorialEstadoPublic.model_validate(h) for h in historial],
        )

    def _descontar_stock_ingredientes(self, uow, producto_id: int, cantidad_productos: int) -> None:
        """
        Por cada ingrediente del producto, descontamos del stock del ingrediente
        la cantidad usada multiplicada por cuántas unidades del producto se pidieron.

        Ej: pizza usa 200g de harina, se piden 3 pizzas → descontamos 600g de harina
        """
        ingredientes_del_producto = uow.producto_ingredientes.get_by_producto(producto_id)

        for pi in ingredientes_del_producto:
            ingrediente = uow.ingredientes.get_by_id(pi.ingrediente_id)
            if not ingrediente:
                continue

            cantidad_a_descontar = pi.cantidad * cantidad_productos

            if ingrediente.stock_cantidad < cantidad_a_descontar:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Stock insuficiente del ingrediente '{ingrediente.nombre}'. "
                        f"Disponible: {ingrediente.stock_cantidad}, "
                        f"necesario: {cantidad_a_descontar}"
                    ),
                )

            ingrediente.stock_cantidad -= cantidad_a_descontar
            uow.ingredientes.add(ingrediente)

    def create(self, data: PedidoCreate, usuario_id: int) -> PedidoConDetalle:
        with PedidoUnitOfWork(self._session) as uow:
            forma = uow.formas_pago.get_by_codigo(data.forma_pago_codigo)
            if not forma or not forma.habilitado:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"Forma de pago '{data.forma_pago_codigo}' no disponible")

            subtotal = Decimal("0.00")
            detalles = []

            for item in data.items:
                producto = uow.productos.get_by_id(item.producto_id)
                if not producto or producto.deleted_at is not None:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                        detail=f"Producto id={item.producto_id} no encontrado")
                if not producto.disponible:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail=f"Producto '{producto.nombre}' no está disponible")
                if producto.stock_cantidad < item.cantidad:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail=f"Stock insuficiente para '{producto.nombre}'")

                precio = Decimal(str(producto.precio_base))
                subtotal_item = precio * item.cantidad
                subtotal += subtotal_item

                # guardamos el snapshot del precio y nombre al momento de la compra
                detalles.append(DetallePedido(
                    producto_id=item.producto_id,
                    cantidad=item.cantidad,
                    nombre_snapshot=producto.nombre,
                    precio_snapshot=precio,
                    subtotal_snap=subtotal_item,
                    personalizacion=item.personalizacion,
                ))

                # descontamos el stock del producto terminado
                producto.stock_cantidad -= item.cantidad
                uow.productos.add(producto)

                # también descontamos el stock de los ingredientes usados para fabricarlo
                self._descontar_stock_ingredientes(uow, item.producto_id, item.cantidad)

            costo_envio = Decimal("50.00") if data.direccion_id else Decimal("0.00")
            total = subtotal + costo_envio

            pedido = Pedido(
                usuario_id=usuario_id,
                direccion_id=data.direccion_id,
                estado_codigo="pendiente",
                forma_pago_codigo=data.forma_pago_codigo,
                subtotal=subtotal,
                descuento=Decimal("0.00"),
                costo_envio=costo_envio,
                total=total,
                notas=data.notas,
            )
            uow.pedidos.add(pedido)

            for detalle in detalles:
                detalle.pedido_id = pedido.id
                uow.detalles.add(detalle)

            # primer registro del historial, estado_desde=None porque es la creación
            uow.historial.add(HistorialEstadoPedido(
                pedido_id=pedido.id,
                estado_desde=None,
                estado_hacia="pendiente",
                usuario_id=usuario_id,
            ))

            result = self._build_detalle(uow, pedido)
        return result

    def get_by_id(self, pedido_id: int, usuario_id: int, roles: list[str]) -> PedidoConDetalle:
        with PedidoUnitOfWork(self._session) as uow:
            pedido = self._get_or_404(uow, pedido_id)
            # un cliente solo puede ver sus propios pedidos
            if "CLIENT" in roles and "ADMIN" not in roles and "PEDIDOS" not in roles:
                if pedido.usuario_id != usuario_id:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                        detail="No tenés permisos para ver este pedido")
            result = self._build_detalle(uow, pedido)
        return result

    def update(self, pedido_id: int, data: "PedidoUpdate", usuario_id: int, roles: list[str]) -> PedidoConDetalle:
        if data.estado_hacia:
            return self.avanzar_estado(pedido_id, data, usuario_id=usuario_id, roles=roles)

        with PedidoUnitOfWork(self._session) as uow:
            pedido = self._get_or_404(uow, pedido_id)
            if data.notas is not None:
                if pedido.usuario_id != usuario_id and "ADMIN" not in roles and "PEDIDOS" not in roles:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="No tenés permisos para modificar este pedido",
                    )
                pedido.notas = data.notas
                pedido.updated_at = datetime.now(timezone.utc)
                uow.pedidos.add(pedido)
            result = self._build_detalle(uow, pedido)
        return result

    def list_mis_pedidos(self, usuario_id: int, offset: int, limit: int) -> PedidoList:
        with PedidoUnitOfWork(self._session) as uow:
            pedidos = uow.pedidos.get_by_usuario(usuario_id, offset=offset, limit=limit)
            total = uow.pedidos.count_by_usuario(usuario_id)
        return PedidoList(
            data=[PedidoPublic.model_validate(p) for p in pedidos],
            total=total,
        )

    def list_all(self, offset: int, limit: int) -> PedidoList:
        with PedidoUnitOfWork(self._session) as uow:
            pedidos = uow.pedidos.get_active(offset=offset, limit=limit)
            total = uow.pedidos.count()
        return PedidoList(
            data=[PedidoPublic.model_validate(p) for p in pedidos],
            total=total,
        )

    def avanzar_estado(
        self,
        pedido_id: int,
        data: AvanzarEstadoRequest,
        usuario_id: int,
        roles: list[str],
    ) -> PedidoConDetalle:
        with PedidoUnitOfWork(self._session) as uow:
            pedido = self._get_or_404(uow, pedido_id)
            estado_actual = pedido.estado_codigo
            estado_hacia = data.estado_hacia

            # validamos que la transición sea válida en la FSM
            transiciones = FSM.get(estado_actual, [])
            if estado_hacia not in transiciones:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=(
                        f"Transición inválida: '{estado_actual}' → '{estado_hacia}'. "
                        f"Transiciones permitidas: {transiciones}"
                    ),
                )

            # cancelar desde en_preparacion requiere rol especial
            if estado_actual in CANCELACION_RESTRINGIDA and estado_hacia == "cancelado":
                if "ADMIN" not in roles and "PEDIDOS" not in roles:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Solo ADMIN o PEDIDOS pueden cancelar un pedido en preparación",
                    )

            # siempre pedimos motivo al cancelar
            if estado_hacia == "cancelado" and not data.motivo:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Se requiere un motivo para cancelar el pedido",
                )

            pedido.estado_codigo = estado_hacia
            pedido.updated_at = datetime.now(timezone.utc)
            uow.pedidos.add(pedido)

            # registramos el cambio en el historial, que es append-only
            uow.historial.add(HistorialEstadoPedido(
                pedido_id=pedido.id,
                estado_desde=estado_actual,
                estado_hacia=estado_hacia,
                usuario_id=usuario_id,
                motivo=data.motivo,
            ))

            result = self._build_detalle(uow, pedido)
        return result

    def list_estados(self) -> list[EstadoPedidoPublic]:
        with PedidoUnitOfWork(self._session) as uow:
            estados = uow.estados.get_all_estados()
            result = [EstadoPedidoPublic.model_validate(e) for e in estados]
        return result

    def list_formas_pago(self) -> list[FormaPagoPublic]:
        with PedidoUnitOfWork(self._session) as uow:
            formas = uow.formas_pago.get_habilitadas()
            result = [FormaPagoPublic.model_validate(f) for f in formas]
        return result
