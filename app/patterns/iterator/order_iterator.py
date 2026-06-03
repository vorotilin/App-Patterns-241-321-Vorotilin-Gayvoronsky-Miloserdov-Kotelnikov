"""
Iterator Pattern: обход дерева заказов без раскрытия его структуры.

OrderIterator — обходит всё дерево в глубину (DFS), возвращая только листья.
FilterIterator — обёртка, пропускает только листья с нужным статусом.

Клиент получает итератор через create_iterator() и вызывает next() / has_next(),
не зная ничего о структуре OrderGroup/OrderLeaf.
"""

from app.patterns.composite.order_composite import OrderComponent, OrderGroup, OrderLeaf


class OrderIterator:
    """Обходит дерево в глубину, возвращает листья (одиночные заказы)."""

    def __init__(self, root: OrderComponent):
        self._leaves: list[OrderLeaf] = []
        self._index = 0
        self._collect(root)

    def _collect(self, node: OrderComponent) -> None:
        if isinstance(node, OrderLeaf):
            self._leaves.append(node)
        elif isinstance(node, OrderGroup):
            for child in node.get_children():
                self._collect(child)

    def has_next(self) -> bool:
        return self._index < len(self._leaves)

    def next(self) -> OrderLeaf:
        leaf = self._leaves[self._index]
        self._index += 1
        return leaf

    def reset(self) -> None:
        self._index = 0

    def __iter__(self):
        self.reset()
        return self

    def __next__(self) -> OrderLeaf:
        if not self.has_next():
            raise StopIteration
        return self.next()

    def __len__(self) -> int:
        return len(self._leaves)


class FilterIterator:
    """
    Декорирующий итератор: фильтрует листья по заданному статусу.
    Демонстрирует, что итераторы можно компоновать.
    """

    def __init__(self, iterator: OrderIterator, status_filter: str):
        self._items = [
            leaf for leaf in iterator
            if leaf.order.status == status_filter
        ]
        self._index = 0

    def has_next(self) -> bool:
        return self._index < len(self._items)

    def next(self) -> OrderLeaf:
        leaf = self._items[self._index]
        self._index += 1
        return leaf

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self) -> OrderLeaf:
        if not self.has_next():
            raise StopIteration
        return self.next()

    def __len__(self) -> int:
        return len(self._items)
