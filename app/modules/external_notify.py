"""
Внешний модуль уведомлений — симулирует стороннее API.
Имеет собственный интерфейс, несовместимый с OrderObserver.
"""


class ExternalSMSGateway:
    """Сторонний сервис SMS-рассылки со своим интерфейсом."""

    def send_message(self, recipient_phone: str, text: str) -> dict:
        return {
            "gateway": "ExternalSMSGateway",
            "phone": recipient_phone,
            "text": text,
            "status": "delivered",
        }

    def bulk_send(self, recipients: list[str], text: str) -> list[dict]:
        return [self.send_message(phone, text) for phone in recipients]


class ExternalEmailService:
    """Сторонний почтовый сервис со своим интерфейсом."""

    def dispatch(self, to_address: str, subject: str, body: str) -> dict:
        return {
            "service": "ExternalEmailService",
            "to": to_address,
            "subject": subject,
            "body": body,
            "status": "sent",
        }
