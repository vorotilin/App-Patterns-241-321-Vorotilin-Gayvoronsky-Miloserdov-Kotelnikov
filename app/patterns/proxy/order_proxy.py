from abc import ABC, abstractmethod


class OrderServiceInterface(ABC):
    @abstractmethod
    def get_order(self, order_id: int):
        pass

    @abstractmethod
    def update_status(self, order_id: int, new_status: str, role: str):
        pass

    @abstractmethod
    def cancel_order(self, order_id: int, role: str):
        pass


class RealOrderService(OrderServiceInterface):
    def get_order(self, order_id: int):
        from app.models import Order
        return Order.objects.get(id=order_id)

    def update_status(self, order_id: int, new_status: str, role: str):
        from app.models import Order
        order = Order.objects.get(id=order_id)
        order.status = new_status
        order.save()
        return order

    def cancel_order(self, order_id: int, role: str):
        from app.models import Order
        order = Order.objects.get(id=order_id)
        order.cancel_order()
        return order


class OrderServiceProxy(OrderServiceInterface):
    ROLE_PERMISSIONS = {
        'admin':   {'get', 'update_status', 'cancel'},
        'courier': {'get', 'update_status'},
        'client':  {'get', 'cancel'},
        'guest':   {'get'},
    }

    def __init__(self):
        self._service = RealOrderService()
        self.access_log: list[str] = []

    def _check(self, role: str, action: str) -> bool:
        allowed = self.ROLE_PERMISSIONS.get(role, set())
        return action in allowed

    def _log(self, role: str, action: str, order_id: int, granted: bool):
        status = "РАЗРЕШЕНО" if granted else "ОТКАЗАНО"
        self.access_log.append(f"[{status}] роль={role} действие={action} заказ=#{order_id}")

    def get_order(self, order_id: int):
        return self._service.get_order(order_id)

    def update_status(self, order_id: int, new_status: str, role: str):
        granted = self._check(role, 'update_status')
        self._log(role, 'update_status', order_id, granted)
        if not granted:
            raise PermissionError(f"Роль '{role}' не может менять статус заказа")
        return self._service.update_status(order_id, new_status, role)

    def cancel_order(self, order_id: int, role: str):
        granted = self._check(role, 'cancel')
        self._log(role, 'cancel', order_id, granted)
        if not granted:
            raise PermissionError(f"Роль '{role}' не может отменять заказы")
        return self._service.cancel_order(order_id, role)
