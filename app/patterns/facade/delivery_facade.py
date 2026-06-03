"""
Facade Pattern: единая точка входа для клиентского кода.

DeliverySystemFacade скрывает сложность взаимодействия между
фабриками, декораторами, шаблонным методом, наблюдателем и командами.
Клиент вызывает один метод — фасад координирует все подсистемы.
"""

from decimal import Decimal
from app.patterns.singleton.logger import Logger
from app.patterns.abstract_factory.order_factory import (
    StandardOrderFactory, ExpressOrderFactory,
    EconomyOrderFactory, PremiumOrderFactory,
)
from app.patterns.decorator.order_decorator import (
    InsuranceDecorator, PriorityDecorator, SMSNotifyDecorator,
    GiftWrapDecorator, FragileDecorator, SignatureRequiredDecorator, PackageDecorator,
)
from app.patterns.observer.order_observer import (
    OrderSubject, ClientNotifier, CourierNotifier, LoggerObserver,
)
from app.patterns.command.order_command import NextStateCommand, CommandHistory
from app.patterns.template_method.delivery_process import (
    StandardDelivery, ExpressDelivery, EconomyDelivery,
)

FACTORY_MAP = {
    "standard": StandardOrderFactory,
    "express": ExpressOrderFactory,
    "economy": EconomyOrderFactory,
    "premium": PremiumOrderFactory,
}

DECORATOR_MAP = {
    "insurance": InsuranceDecorator,
    "priority": PriorityDecorator,
    "sms": SMSNotifyDecorator,
    "gift_wrap": GiftWrapDecorator,
    "fragile": FragileDecorator,
    "signature": SignatureRequiredDecorator,
    "package": PackageDecorator,
}

PROCESS_MAP = {
    "standard": StandardDelivery,
    "express": ExpressDelivery,
    "economy": EconomyDelivery,
}


class DeliverySystemFacade:
    """
    Фасад системы доставки.
    Предоставляет упрощённый интерфейс к набору подсистем.
    """

    def __init__(self):
        self._logger = Logger()
        self._history = CommandHistory()

    def create_order(
        self,
        user,
        pickup_address: str,
        delivery_address: str,
        factory_type: str = "standard",
        decorator_keys: list[str] | None = None,
        cargo_type: str = "document",
    ) -> dict:
        """
        Создаёт заказ через фабрику, применяет декораторы,
        запускает шаблонный процесс и уведомляет наблюдателей.
        Возвращает словарь с результатами всех шагов.
        """
        self._logger.log(f"[Facade] Начало создания заказа ({factory_type})")
        steps = []

        # если выбрана посылка — декоратор package включается автоматически
        if cargo_type == 'package':
            decorator_keys = list(decorator_keys or [])
            if 'package' not in decorator_keys:
                decorator_keys.append('package')

        # 1. Abstract Factory
        factory_cls = FACTORY_MAP.get(factory_type, StandardOrderFactory)
        factory = factory_cls()
        order = factory.create_order(
            user=user,
            pickup_address=pickup_address,
            delivery_address=delivery_address,
            cargo_type=cargo_type,
        )
        payment = factory.create_payment(order, order.price)
        tracking = factory.create_tracking(order)
        steps.append(f"[AbstractFactory:{factory_type}] Заказ #{order.id} создан, оплата {payment.method}, трекинг: {tracking.status}")

        # 2. Decorator
        decorated = order
        applied_decorators = []
        for key in (decorator_keys or []):
            dec_cls = DECORATOR_MAP.get(key)
            if dec_cls:
                decorated = dec_cls(decorated)
                applied_decorators.append(key)
        final_price = decorated.get_price() if hasattr(decorated, 'get_price') else order.price
        if applied_decorators:
            order.price = final_price
            order.save()
            steps.append(f"[Decorator] Применены: {', '.join(applied_decorators)}, итоговая цена: {final_price} руб.")

        # 3. Observer
        subject = OrderSubject()
        client_obs = ClientNotifier()
        courier_obs = CourierNotifier()
        logger_obs = LoggerObserver()
        subject.attach(client_obs)
        subject.attach(courier_obs)
        subject.attach(logger_obs)
        subject.notify(order, f"Заказ #{order.id} принят в обработку ({factory_type})")
        notifications = client_obs.notifications + courier_obs.notifications + logger_obs.log
        steps.append(f"[Observer] Отправлено уведомлений: {len(notifications)}")

        # 4. Command — переход к следующему статусу
        cmd = NextStateCommand(order)
        self._history.execute(cmd)
        order.refresh_from_db()
        steps.append(f"[Command] Статус заказа: {order.get_status_display()}")

        self._logger.log(f"[Facade] Заказ #{order.id} обработан через {len(steps)} шагов")

        return {
            "order": order,
            "payment": payment,
            "tracking": tracking,
            "factory_type": factory_type,
            "applied_decorators": applied_decorators,
            "final_price": final_price,
            "notifications": notifications,
            "steps": steps,
        }

    def get_order_summary(self, order_id: int) -> dict:
        """Возвращает краткую сводку по заказу."""
        from app.models import Order
        order = Order.objects.select_related('user', 'courier').get(id=order_id)
        return {
            "id": order.id,
            "status": order.get_status_display(),
            "tariff": order.get_tariff_display(),
            "price": order.price,
            "user": order.user.username,
            "courier": order.courier.user.username if order.courier else "не назначен",
        }
