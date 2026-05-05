"""
Decorator Pattern: динамическое добавление возможностей к заказу
"""

from decimal import Decimal


class OrderDecorator:
    """Базовый декоратор для заказа"""
    
    def __init__(self, order):
        self.order = order
    
    def get_price(self):
        """Получить цену - для другого декоратора вызовет его get_price()"""
        if hasattr(self.order, 'get_price'):
            return self.order.get_price()
        return self.order.price
    
    def get_description(self):
        return f"Заказ #{self.order.id}"


class InsuranceDecorator(OrderDecorator):
    """Декоратор: добавление страховки"""
    
    def get_price(self):
        base_price = self.order.get_price() if hasattr(self.order, 'get_price') else self.order.price
        return base_price + Decimal(500)
    
    def get_description(self):
        base = self.order.get_description() if hasattr(self.order, 'get_description') else f"Заказ #{self.order.id}"
        if isinstance(self.order, OrderDecorator):
            base = self.order.get_description()
        return f"{base} + Страховка"


class PriorityDecorator(OrderDecorator):
    """Декоратор: приоритетная доставка"""
    
    def get_price(self):
        base_price = self.order.get_price() if hasattr(self.order, 'get_price') else self.order.price
        return base_price * Decimal('1.3')
    
    def get_description(self):
        base = self.order.get_description() if hasattr(self.order, 'get_description') else f"Заказ #{self.order.id}"
        if isinstance(self.order, OrderDecorator):
            base = self.order.get_description()
        return f"{base} + Приоритет (30% надбавка)"


class SMSNotifyDecorator(OrderDecorator):
    """Декоратор: SMS уведомления"""
    
    def get_price(self):
        base_price = self.order.get_price() if hasattr(self.order, 'get_price') else self.order.price
        return base_price + Decimal(100)
    
    def get_description(self):
        base = self.order.get_description() if hasattr(self.order, 'get_description') else f"Заказ #{self.order.id}"
        if isinstance(self.order, OrderDecorator):
            base = self.order.get_description()
        return f"{base} + SMS-уведомления"


class GiftWrapDecorator(OrderDecorator):
    """Декоратор: подарочная упаковка"""
    
    def get_price(self):
        base_price = self.order.get_price() if hasattr(self.order, 'get_price') else self.order.price
        return base_price + Decimal(300)
    
    def get_description(self):
        base = self.order.get_description() if hasattr(self.order, 'get_description') else f"Заказ #{self.order.id}"
        if isinstance(self.order, OrderDecorator):
            base = self.order.get_description()
        return f"{base} + Подарочная упаковка"


class FragileDecorator(OrderDecorator):
    """Декоратор: хрупкий товар (осторожная доставка)"""
    
    def get_price(self):
        base_price = self.order.get_price() if hasattr(self.order, 'get_price') else self.order.price
        return base_price + Decimal(800)
    
    def get_description(self):
        base = self.order.get_description() if hasattr(self.order, 'get_description') else f"Заказ #{self.order.id}"
        if isinstance(self.order, OrderDecorator):
            base = self.order.get_description()
        return f"{base} + Хрупкий товар (осторожная доставка)"


class SignatureRequiredDecorator(OrderDecorator):
    """Декоратор: требуется подпись при доставке"""
    
    def get_price(self):
        base_price = self.order.get_price() if hasattr(self.order, 'get_price') else self.order.price
        return base_price + Decimal(200)
    
    def get_description(self):
        base = self.order.get_description() if hasattr(self.order, 'get_description') else f"Заказ #{self.order.id}"
        if isinstance(self.order, OrderDecorator):
            base = self.order.get_description()
        return f"{base} + Требуется подпись"
