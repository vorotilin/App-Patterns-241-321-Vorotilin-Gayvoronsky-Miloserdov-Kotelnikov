from abc import ABC, abstractmethod


class OrderObserver(ABC):
    @abstractmethod
    def update(self, order, event: str):
        pass


class OrderSubject:
    def __init__(self):
        self._observers: list[OrderObserver] = []

    def attach(self, observer: OrderObserver):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: OrderObserver):
        self._observers.remove(observer)

    def notify(self, order, event: str):
        for observer in self._observers:
            observer.update(order, event)


class ClientNotifier(OrderObserver):
    def __init__(self):
        self.notifications: list[str] = []

    def update(self, order, event: str):
        msg = f"[Клиент {order.user.username}] Заказ #{order.id}: {event}"
        self.notifications.append(msg)


class CourierNotifier(OrderObserver):
    def __init__(self):
        self.notifications: list[str] = []

    def update(self, order, event: str):
        courier_name = order.courier.user.username if order.courier else "не назначен"
        msg = f"[Курьер {courier_name}] Заказ #{order.id}: {event}"
        self.notifications.append(msg)


class LoggerObserver(OrderObserver):
    def __init__(self):
        self.log: list[str] = []

    def update(self, order, event: str):
        msg = f"[Лог] Заказ #{order.id} | {event}"
        self.log.append(msg)
