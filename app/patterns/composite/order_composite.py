"""
Composite Pattern: единообразная работа с деревом заказов.

OrderComponent — общий интерфейс для листьев и контейнеров.
OrderLeaf      — одиночный заказ (лист дерева).
OrderGroup     — группа заказов или подгрупп (ветвь/корень).

Клиентский код вызывает get_total_price() и get_count()
одинаково на любом уровне иерархии.
"""

from abc import ABC, abstractmethod
from decimal import Decimal


class OrderComponent(ABC):
    """Абстрактный компонент дерева заказов."""

    @abstractmethod
    def get_total_price(self) -> Decimal:
        pass

    @abstractmethod
    def get_count(self) -> int:
        pass

    @abstractmethod
    def display(self, indent: int = 0) -> list[dict]:
        """Возвращает список строк для отображения дерева."""
        pass


class OrderLeaf(OrderComponent):
    """Лист — одиночный заказ."""

    def __init__(self, order):
        self._order = order

    @property
    def order(self):
        return self._order

    def get_total_price(self) -> Decimal:
        return self._order.price

    def get_count(self) -> int:
        return 1

    def display(self, indent: int = 0) -> list[dict]:
        return [{
            "indent": indent,
            "indent_px": indent * 24,
            "text": (
                f"Заказ #{self._order.id}"
                f" [{self._order.get_tariff_display()}]"
                f" {self._order.get_status_display()}"
                f" — {self._order.price} руб."
            ),
            "is_group": False,
        }]


class OrderGroup(OrderComponent):
    """Группа — может содержать листья и другие группы."""

    def __init__(self, name: str):
        self.name = name
        self._children: list[OrderComponent] = []

    def add(self, component: OrderComponent) -> None:
        self._children.append(component)

    def remove(self, component: OrderComponent) -> None:
        self._children.remove(component)

    def get_children(self) -> list[OrderComponent]:
        return list(self._children)

    def get_total_price(self) -> Decimal:
        return sum((c.get_total_price() for c in self._children), Decimal(0))

    def get_count(self) -> int:
        return sum(c.get_count() for c in self._children)

    def display(self, indent: int = 0) -> list[dict]:
        rows = [{
            "indent": indent,
            "indent_px": indent * 24,
            "text": f"{self.name}  (заказов: {self.get_count()}, сумма: {self.get_total_price()} руб.)",
            "is_group": True,
        }]
        for child in self._children:
            rows.extend(child.display(indent + 1))
        return rows


def build_tree_from_db() -> OrderGroup:
    """
    Строит дерево из БД: корень → группы по тарифу → группы по статусу → листья.
    """
    from app.models import Order

    root = OrderGroup("Все заказы")

    tariff_labels = {
        "economy": "Эконом",
        "standard": "Стандарт",
        "express": "Экспресс",
    }
    status_labels = {
        "new": "Новые",
        "payment_pending": "Ожидают оплаты",
        "courier_assigned": "Курьер назначен",
        "in_delivery": "В доставке",
        "delivered": "Доставлены",
        "cancelled": "Отменены",
    }

    tariff_groups: dict[str, OrderGroup] = {}
    status_groups: dict[str, dict[str, OrderGroup]] = {}

    for order in Order.objects.select_related("user").order_by("id"):
        t = order.tariff
        s = order.status

        if t not in tariff_groups:
            tg = OrderGroup(tariff_labels.get(t, t))
            tariff_groups[t] = tg
            status_groups[t] = {}
            root.add(tg)

        if s not in status_groups[t]:
            sg = OrderGroup(status_labels.get(s, s))
            status_groups[t][s] = sg
            tariff_groups[t].add(sg)

        status_groups[t][s].add(OrderLeaf(order))

    return root
