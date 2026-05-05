from abc import ABC, abstractmethod

class OrderState(ABC):
    @abstractmethod
    def next(self, order):
        pass
    
    @abstractmethod
    def cancel(self, order):
        pass
    
    @abstractmethod
    def get_status(self):
        pass

class NewOrderState(OrderState):
    def next(self, order):
        from .order_state import PaymentPendingState
        order.state = PaymentPendingState()
        order.status = 'payment_pending'
        order.save()
    
    def cancel(self, order):
        from .order_state import CancelledState
        order.state = CancelledState()
        order.status = 'cancelled'
        order.save()
    
    def get_status(self):
        return "Новый заказ"

class PaymentPendingState(OrderState):
    def next(self, order):
        from .order_state import CourierAssignedState
        order.state = CourierAssignedState()
        order.status = 'courier_assigned'
        order.save()
    
    def cancel(self, order):
        from .order_state import CancelledState
        order.state = CancelledState()
        order.status = 'cancelled'
        order.save()
    
    def get_status(self):
        return "Ожидает оплаты"

class CourierAssignedState(OrderState):
    def next(self, order):
        from .order_state import InDeliveryState
        order.state = InDeliveryState()
        order.status = 'in_delivery'
        order.save()
    
    def cancel(self, order):
        from .order_state import CancelledState
        order.state = CancelledState()
        order.status = 'cancelled'
        order.save()
    
    def get_status(self):
        return "Курьер назначен"

class InDeliveryState(OrderState):
    def next(self, order):
        from .order_state import DeliveredState
        order.state = DeliveredState()
        order.status = 'delivered'
        order.save()
    
    def cancel(self, order):
        from .order_state import CancelledState
        order.state = CancelledState()
        order.status = 'cancelled'
        order.save()
    
    def get_status(self):
        return "В доставке"

class DeliveredState(OrderState):
    def next(self, order):
        print("Заказ уже доставлен")
    
    def cancel(self, order):
        print("Нельзя отменить доставленный заказ")
    
    def get_status(self):
        return "Доставлен"

class CancelledState(OrderState):
    def next(self, order):
        print("Отменённый заказ нельзя изменить")
    
    def cancel(self, order):
        print("Заказ уже отменён")
    
    def get_status(self):
        return "Отменён"