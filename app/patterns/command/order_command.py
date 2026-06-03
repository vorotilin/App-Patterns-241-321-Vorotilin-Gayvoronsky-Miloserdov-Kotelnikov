from abc import ABC, abstractmethod


class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass

    @abstractmethod
    def description(self) -> str:
        pass


class NextStateCommand(Command):
    def __init__(self, order):
        self._order = order
        self._prev_status = order.status

    def execute(self):
        self._prev_status = self._order.status
        self._order.next_state()

    def undo(self):
        self._order.status = self._prev_status
        self._order._order_state = None
        self._order.save()

    def description(self) -> str:
        return f"Заказ #{self._order.id}: переход статуса"


class CancelOrderCommand(Command):
    def __init__(self, order):
        self._order = order
        self._prev_status = order.status

    def execute(self):
        self._prev_status = self._order.status
        self._order.cancel_order()

    def undo(self):
        self._order.status = self._prev_status
        self._order._order_state = None
        self._order.save()

    def description(self) -> str:
        return f"Заказ #{self._order.id}: отмена"


class AssignCourierCommand(Command):
    def __init__(self, order, courier):
        self._order = order
        self._courier = courier
        self._prev_courier = order.courier

    def execute(self):
        self._prev_courier = self._order.courier
        self._order.courier = self._courier
        self._order.save()

    def undo(self):
        self._order.courier = self._prev_courier
        self._order.save()

    def description(self) -> str:
        return f"Заказ #{self._order.id}: назначен курьер {self._courier.user.username}"


class CommandHistory:
    def __init__(self):
        self._history: list[Command] = []

    def execute(self, command: Command):
        command.execute()
        self._history.append(command)

    def undo(self):
        if not self._history:
            return None
        command = self._history.pop()
        command.undo()
        return command

    def get_history(self) -> list[Command]:
        return list(self._history)
