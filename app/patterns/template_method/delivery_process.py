"""
Template Method Pattern: базовый процесс доставки с переопределяемыми шагами
"""

from abc import ABC, abstractmethod
from app.patterns.singleton.logger import Logger
from app.math_models.shortest_path import ShortestPathFinder


class BaseDeliveryProcess(ABC):
    """Абстрактный базовый класс доставки"""
    
    def __init__(self):
        self.logger = Logger()
        self.path_finder = ShortestPathFinder()
    
    def execute(self, order):
        """Шаблонный метод - определяет последовательность шагов"""
        try:
            self.validate_order(order)
            self.calculate_price(order)
            self.process_payment(order)
            self.assign_courier(order)
            self.notify_client(order)
            self.logger.log(f"Заказ #{order.id} успешно обработан")
        except Exception as e:
            self.logger.log(f"Ошибка: {str(e)}")
            raise
    
    @abstractmethod
    def validate_order(self, order):
        """Абстрактный метод - проверка заказа"""
        pass
    
    def calculate_price(self, order):
        order.apply_tariff()
        order.save()
        self.logger.log(f"Цена: {order.price} руб. (тариф={order.tariff}, расстояние={order.distance_km} км)")
    
    @abstractmethod
    def process_payment(self, order):
        """Абстрактный метод - обработка платежа"""
        pass
    
    @abstractmethod
    def assign_courier(self, order):
        """Абстрактный метод - назначение курьера"""
        pass
    
    def notify_client(self, order):
        """Конкретный метод - уведомление клиента"""
        self.logger.log(f"Уведомлен {order.user.username}")


class StandardDelivery(BaseDeliveryProcess):
    """Стандартная доставка"""
    
    def validate_order(self, order):
        self.logger.log(f"Стандартная проверка заказа #{order.id}")
        if not order.pickup_address or not order.delivery_address:
            raise ValueError("Адреса не заполнены")
    
    def process_payment(self, order):
        self.logger.log(f"Обычная оплата заказа #{order.id}")
        from app.models import Payment
        Payment.objects.create(order=order, amount=order.price, method="card")
    
    def assign_courier(self, order):
        self.logger.log(f"Назначен ближайший курьер")
        from app.models import Courier
        courier = Courier.objects.filter(is_available=True).first()
        if courier:
            order.courier = courier
            order.save()


class ExpressDelivery(BaseDeliveryProcess):
    """Экспресс-доставка"""
    
    def validate_order(self, order):
        self.logger.log(f"Минимальная проверка экспресс-заказа #{order.id}")
    
    def process_payment(self, order):
        self.logger.log(f"Мгновенная оплата экспресс-заказа #{order.id}")
        from app.models import Payment
        Payment.objects.create(order=order, amount=order.price, method="instant")
    
    def assign_courier(self, order):
        self.logger.log(f"Назначен топ-курьер")
        from app.models import Courier
        courier = Courier.objects.filter(is_available=True, rating__gte=4.5).first()
        if courier:
            order.courier = courier
            order.save()


class EconomyDelivery(BaseDeliveryProcess):
    """Экономная доставка"""
    
    def validate_order(self, order):
        self.logger.log(f"Базовая проверка экономного заказа #{order.id}")
    
    def process_payment(self, order):
        self.logger.log(f"Оплата экономного заказа #{order.id}")
        from app.models import Payment
        Payment.objects.create(order=order, amount=order.price, method="cash")
    
    def assign_courier(self, order):
        self.logger.log(f"Назначен первый свободный курьер")
        from app.models import Courier
        courier = Courier.objects.filter(is_available=True).first()
        if courier:
            order.courier = courier
            order.save()
