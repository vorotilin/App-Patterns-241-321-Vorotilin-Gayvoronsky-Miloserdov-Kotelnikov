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
        order.state = PaymentPendingState()
        order.status = 'payment_pending'
        order.state_name = 'PaymentPendingState'
        order.save()

    def cancel(self, order):
        order.state = CancelledState()
        order.status = 'cancelled'
        order.state_name = 'CancelledState'
        order.save()

    def get_status(self):
        return "Новый заказ"

class PaymentPendingState(OrderState):
    def next(self, order):
        order.state = CourierAssignedState()
        order.status = 'courier_assigned'
        order.state_name = 'CourierAssignedState'
        order.save()

    def cancel(self, order):
        order.state = CancelledState()
        order.status = 'cancelled'
        order.state_name = 'CancelledState'
        order.save()

    def get_status(self):
        return "Ожидает оплаты"

class CourierAssignedState(OrderState):
    def next(self, order):
        order.state = InDeliveryState()
        order.status = 'in_delivery'
        order.state_name = 'InDeliveryState'
        order.save()

    def cancel(self, order):
        order.state = CancelledState()
        order.status = 'cancelled'
        order.state_name = 'CancelledState'
        order.save()

    def get_status(self):
        return "Курьер назначен"

class InDeliveryState(OrderState):
    def next(self, order):
        order.state = DeliveredState()
        order.status = 'delivered'
        order.state_name = 'DeliveredState'
        order.save()

    def cancel(self, order):
        order.state = CancelledState()
        order.status = 'cancelled'
        order.state_name = 'CancelledState'
        order.save()

    def get_status(self):
        return "В доставке"

class DeliveredState(OrderState):
    def next(self, order):
        pass

    def cancel(self, order):
        pass

    def get_status(self):
        return "Доставлен"

class CancelledState(OrderState):
    def next(self, order):
        pass

    def cancel(self, order):
        pass

    def get_status(self):
        return "Отменён"