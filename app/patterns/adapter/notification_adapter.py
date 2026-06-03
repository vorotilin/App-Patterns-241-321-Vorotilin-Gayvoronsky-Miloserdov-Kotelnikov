"""
Adapter Pattern: адаптирует внешние сервисы уведомлений
к интерфейсу OrderObserver, используемому в системе.

Проблема: ExternalSMSGateway и ExternalEmailService имеют свои
интерфейсы (send_message/dispatch), несовместимые с OrderObserver.update().
Адаптеры оборачивают их, реализуя нужный интерфейс без изменения оригиналов.
"""

from app.patterns.observer.order_observer import OrderObserver
from app.modules.external_notify import ExternalSMSGateway, ExternalEmailService


class SMSGatewayAdapter(OrderObserver):
    """Адаптирует ExternalSMSGateway к интерфейсу OrderObserver."""

    def __init__(self):
        self._gateway = ExternalSMSGateway()
        self.sent: list[dict] = []

    def update(self, order, event: str):
        phone = getattr(order.user, 'phone', None) or "+7-000-000-0000"
        text = f"Заказ #{order.id}: {event}"
        result = self._gateway.send_message(phone, text)
        self.sent.append(result)


class EmailServiceAdapter(OrderObserver):
    """Адаптирует ExternalEmailService к интерфейсу OrderObserver."""

    def __init__(self):
        self._service = ExternalEmailService()
        self.sent: list[dict] = []

    def update(self, order, event: str):
        email = order.user.email or "no-reply@delivery.local"
        subject = f"Обновление по заказу #{order.id}"
        body = f"Статус: {event}\nАдрес доставки: {order.delivery_address}"
        result = self._service.dispatch(email, subject, body)
        self.sent.append(result)
