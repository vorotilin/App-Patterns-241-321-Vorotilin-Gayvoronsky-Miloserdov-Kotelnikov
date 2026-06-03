from django.contrib.auth.models import AbstractUser
from django.db import models


# ==================== ПОЛЬЗОВАТЕЛИ ====================

class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.username


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client')
    
    def __str__(self):
        return f"Client: {self.user.username}"


class Courier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='courier')
    vehicle = models.CharField(max_length=100, default='Пеший')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Courier: {self.user.username}"



# ==================== ЗАКАЗЫ ====================

class Order(models.Model):
    TARIFF_CHOICES = [
        ('economy', 'Эконом'),
        ('standard', 'Стандарт'),
        ('express', 'Экспресс'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('payment_pending', 'Ожидает оплаты'),
        ('courier_assigned', 'Назначен курьер'),
        ('in_delivery', 'В доставке'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    courier = models.ForeignKey(Courier, on_delete=models.SET_NULL, null=True, blank=True)
    
    pickup_address = models.CharField(max_length=255)
    delivery_address = models.CharField(max_length=255)
    
    tariff = models.CharField(max_length=20, choices=TARIFF_CHOICES, default='economy')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    distance_km = models.FloatField(default=5.0)

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Для паттерна Состояние
    state_name = models.CharField(max_length=50, default='NewOrderState')
    
    @property
    def state(self):
        if not hasattr(self, '_order_state') or self._order_state is None:
            from app.patterns.state.order_state import (
                NewOrderState, PaymentPendingState, CourierAssignedState,
                InDeliveryState, DeliveredState, CancelledState,
            )
            state_map = {
                'new': NewOrderState(),
                'payment_pending': PaymentPendingState(),
                'courier_assigned': CourierAssignedState(),
                'in_delivery': InDeliveryState(),
                'delivered': DeliveredState(),
                'cancelled': CancelledState(),
            }
            self._order_state = state_map.get(self.status, NewOrderState())
        return self._order_state

    @state.setter
    def state(self, value):
        self._order_state = value
    
    def apply_tariff(self):
        from app.patterns.strategy.tariff_strategy import EconomyTariff, StandardTariff, ExpressTariff
        strategy_map = {
            'economy': EconomyTariff(),
            'standard': StandardTariff(),
            'express': ExpressTariff(),
        }
        strategy = strategy_map.get(self.tariff, StandardTariff())
        from decimal import Decimal
        self.price = Decimal(str(strategy.calculate_price(self.distance_km)))

    def next_state(self):
        self.state.next(self)

    def cancel_order(self):
        self.state.cancel(self)

    def __str__(self):
        return f"Order #{self.id}"


# ==================== ТРЕКИНГ ====================

class Tracking(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='tracking')
    status = models.CharField(max_length=100)
    
    def __str__(self):
        return f"Tracking for Order #{self.order.id}: {self.status}"


# ==================== ПЛАТЕЖИ ====================

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20)
    
    def __str__(self):
        return f"Payment #{self.id} - {self.amount} руб."


# ==================== ОТЗЫВЫ ====================

class Review(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='review')
    rating = models.IntegerField()
    
    def __str__(self):
        return f"Review for Order #{self.order.id}: {self.rating}⭐"


# ==================== МАТЕМАТИЧЕСКАЯ МОДЕЛЬ (A*) ====================

class RouteGraph(models.Model):
    from_node = models.CharField(max_length=100)
    to_node = models.CharField(max_length=100)
    distance = models.FloatField()
    
    class Meta:
        unique_together = ('from_node', 'to_node')
    
    def __str__(self):
        return f"{self.from_node} → {self.to_node}: {self.distance} km"