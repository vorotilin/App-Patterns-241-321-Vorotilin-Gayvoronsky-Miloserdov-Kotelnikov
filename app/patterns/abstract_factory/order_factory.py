"""
Abstract Factory Pattern: создание семей связанных объектов
"""

from abc import ABC, abstractmethod
from app.models import Order, Payment, Tracking
from decimal import Decimal


class OrderComponentFactory(ABC):
    """Абстрактная фабрика для создания компонентов заказа"""
    
    @abstractmethod
    def create_order(self, **kwargs):
        """Создание заказа"""
        pass
    
    @abstractmethod
    def create_payment(self, order, amount):
        """Создание платежа"""
        pass
    
    @abstractmethod
    def create_tracking(self, order):
        """Создание трекинга"""
        pass


class StandardOrderFactory(OrderComponentFactory):
    """Фабрика для стандартных заказов"""

    def create_order(self, **kwargs):
        kwargs.setdefault('tariff', 'standard')
        kwargs.setdefault('price', Decimal(0))
        kwargs.setdefault('status', 'new')
        order = Order.objects.create(**kwargs)
        order.apply_tariff()
        order.save()
        return order

    def create_payment(self, order, amount):
        return Payment.objects.create(order=order, amount=amount, method="card")

    def create_tracking(self, order):
        return Tracking.objects.create(order=order, status="Заказ создан")


class ExpressOrderFactory(OrderComponentFactory):
    """Фабрика для экспресс-заказов"""

    def create_order(self, **kwargs):
        kwargs['tariff'] = 'express'
        kwargs['price'] = Decimal(0)
        kwargs['status'] = 'new'
        order = Order.objects.create(**kwargs)
        order.apply_tariff()
        order.save()
        return order

    def create_payment(self, order, amount):
        return Payment.objects.create(order=order, amount=amount, method="instant")

    def create_tracking(self, order):
        return Tracking.objects.create(order=order, status="Экспресс-заказ создан")


class EconomyOrderFactory(OrderComponentFactory):
    """Фабрика для экономных заказов"""

    def create_order(self, **kwargs):
        kwargs['tariff'] = 'economy'
        kwargs['price'] = Decimal(0)
        kwargs['status'] = 'new'
        order = Order.objects.create(**kwargs)
        order.apply_tariff()
        order.save()
        return order

    def create_payment(self, order, amount):
        return Payment.objects.create(order=order, amount=amount, method="cash")

    def create_tracking(self, order):
        return Tracking.objects.create(order=order, status="Экономный заказ создан")


class PremiumOrderFactory(OrderComponentFactory):
    """Фабрика для премиум-заказов — экспресс-тариф с наценкой 50%"""

    def create_order(self, **kwargs):
        kwargs['tariff'] = 'express'
        kwargs['price'] = Decimal(0)
        kwargs['status'] = 'new'
        order = Order.objects.create(**kwargs)
        order.apply_tariff()
        order.price = (order.price * Decimal('1.5')).quantize(Decimal('0.01'))
        order.save()
        return order

    def create_payment(self, order, amount):
        return Payment.objects.create(order=order, amount=amount, method="card")

    def create_tracking(self, order):
        return Tracking.objects.create(order=order, status="Премиум-заказ с приоритетным отслеживанием")
