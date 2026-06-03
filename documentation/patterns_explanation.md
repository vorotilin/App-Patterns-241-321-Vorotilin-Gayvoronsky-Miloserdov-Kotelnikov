# Паттерны проектирования — пояснительная записка

**Проект:** Автоматизированная система доставки документов  
**Группа:** 241-321  
**Команда:** Воротилин, Гайворонский, Милосердов, Котельников

---

## Навигация

| Паттерн | Файл реализации | Демо-страница |
|---------|-----------------|---------------|
| Singleton | [app/patterns/singleton/logger.py](../app/patterns/singleton/logger.py) | `/demo/singleton/` |
| Strategy | [app/patterns/strategy/tariff_strategy.py](../app/patterns/strategy/tariff_strategy.py) | `/demo/strategy/` |
| State | [app/patterns/state/order_state.py](../app/patterns/state/order_state.py) | `/demo/state/` |
| Abstract Factory | [app/patterns/abstract_factory/order_factory.py](../app/patterns/abstract_factory/order_factory.py) | `/demo/factory/` |
| Decorator | [app/patterns/decorator/order_decorator.py](../app/patterns/decorator/order_decorator.py) | `/demo/decorator/` |
| Template Method | [app/patterns/template_method/delivery_process.py](../app/patterns/template_method/delivery_process.py) | `/demo/template-method/` |
| Observer | [app/patterns/observer/order_observer.py](../app/patterns/observer/order_observer.py) | `/demo/observer/` |
| Proxy | [app/patterns/proxy/order_proxy.py](../app/patterns/proxy/order_proxy.py) | `/demo/proxy/` |
| Command | [app/patterns/command/order_command.py](../app/patterns/command/order_command.py) | `/demo/command/` |
| Adapter | [app/patterns/adapter/notification_adapter.py](../app/patterns/adapter/notification_adapter.py) | `/demo/adapter/` |
| Facade | [app/patterns/facade/delivery_facade.py](../app/patterns/facade/delivery_facade.py) | `/demo/facade/` |
| Composite | [app/patterns/composite/order_composite.py](../app/patterns/composite/order_composite.py) | `/demo/composite/` |
| Iterator | [app/patterns/iterator/order_iterator.py](../app/patterns/iterator/order_iterator.py) | `/demo/composite/` |
| A* (Dijkstra) | [app/math_models/shortest_path.py](../app/math_models/shortest_path.py) | `/demo/astar/` |

---

## 1. Singleton (Одиночка)

**Файл:** [app/patterns/singleton/logger.py](../app/patterns/singleton/logger.py)  
**Категория:** Порождающий

### Что делает
Гарантирует, что у класса `Logger` существует ровно один экземпляр во всём приложении. Любой модуль, создающий `Logger()`, получит один и тот же объект — со всей накопленной историей событий.

### Как реализован
Метод `__new__` проверяет наличие атрибута `_instance`. Если он ещё не создан — создаёт экземпляр и сохраняет его в переменной класса. При всех последующих вызовах возвращает уже существующий объект.

```
logger1 = Logger()
logger2 = Logger()
assert logger1 is logger2  # True
```

### Роль в системе
Все части системы (Template Method, Factory, Facade, views) пишут события в один и тот же журнал. Лог доступен на демо-странице `/demo/singleton/`.

---

## 2. Strategy (Стратегия)

**Файл:** [app/patterns/strategy/tariff_strategy.py](../app/patterns/strategy/tariff_strategy.py)  
**Категория:** Поведенческий

### Что делает
Определяет семейство алгоритмов расчёта цены и делает их взаимозаменяемыми. Клиентский код (модель `Order`) работает с абстракцией `TariffStrategy`, не зная, какая именно стратегия выбрана.

### Как реализован
Абстрактный класс `TariffStrategy` задаёт метод `calculate_price(distance_km)`. Три конкретные стратегии реализуют его с разными коэффициентами:

- `EconomyTariff` — 50 руб./км  
- `StandardTariff` — 80 руб./км  
- `ExpressTariff` — 150 руб./км

### Роль в системе
Метод `Order.apply_tariff()` выбирает стратегию по полю `tariff` и пересчитывает цену. Шаблонный метод `BaseDeliveryProcess.calculate_price()` вызывает `apply_tariff()` — стратегию можно заменить, не трогая процесс доставки.

---

## 3. State (Состояние)

**Файл:** [app/patterns/state/order_state.py](../app/patterns/state/order_state.py)  
**Категория:** Поведенческий

### Что делает
Позволяет объекту `Order` менять поведение при изменении его внутреннего состояния. Методы `next_state()` и `cancel_order()` делегируются текущему объекту состояния.

### Как реализован
Абстрактный класс `OrderState` задаёт интерфейс `next(order)`, `cancel(order)`, `get_status()`. Шесть конкретных состояний формируют цепочку:

```
NewOrderState → PaymentPendingState → CourierAssignedState → InDeliveryState → DeliveredState
                        ↓ (из любого)
                   CancelledState
```

Состояние восстанавливается из поля `Order.status` через свойство `Order.state` при каждом обращении.

### Роль в системе
Жизненный цикл заказа. Кнопка «Следующий статус» в карточке заказа и на демо-странице вызывает `order.next_state()`, которое определяет допустимый переход.

---

## 4. Abstract Factory (Абстрактная фабрика)

**Файл:** [app/patterns/abstract_factory/order_factory.py](../app/patterns/abstract_factory/order_factory.py)  
**Категория:** Порождающий

### Что делает
Создаёт семейства связанных объектов (`Order`, `Payment`, `Tracking`) без указания конкретных классов. Каждая фабрика гарантирует согласованность создаваемых объектов.

### Как реализован
Абстрактный класс `OrderComponentFactory` объявляет три метода: `create_order()`, `create_payment()`, `create_tracking()`. Четыре конкретные фабрики реализуют их:

- `StandardOrderFactory` — тариф standard, оплата card  
- `ExpressOrderFactory` — тариф express, цена 7000, оплата instant  
- `EconomyOrderFactory` — тариф economy, цена 2500, оплата cash  
- `PremiumOrderFactory` — тариф express, цена 15000, приоритетный трекинг

### Роль в системе
Фасад `DeliverySystemFacade` и вьюха `demo_factory` используют фабрику для создания заказов. Чтобы добавить новый тип (например, `CorporateOrderFactory`), достаточно написать новый подкласс.

---

## 5. Decorator (Декоратор)

**Файл:** [app/patterns/decorator/order_decorator.py](../app/patterns/decorator/order_decorator.py)  
**Категория:** Структурный

### Что делает
Динамически добавляет к объекту `Order` дополнительные обязанности (дополнительные услуги), оборачивая его в цепочку декораторов. Каждый декоратор делегирует вызов внутреннему объекту и добавляет своё поведение.

### Как реализован
Базовый класс `OrderDecorator` хранит ссылку на декорируемый объект и делегирует `get_price()` и `get_description()`. Шесть конкретных декораторов добавляют надбавки к цене:

- `InsuranceDecorator` — +500 руб.  
- `PriorityDecorator` — ×1.3  
- `SMSNotifyDecorator` — +100 руб.  
- `GiftWrapDecorator` — +300 руб.  
- `FragileDecorator` — +800 руб.  
- `SignatureRequiredDecorator` — +200 руб.

### Роль в системе
На демо-странице `/demo/decorator/` пользователь выбирает заказ и любую комбинацию декораторов. Порядок применения влияет на итоговую цену (PriorityDecorator умножает накопленную сумму). Фасад также поддерживает применение декораторов.

---

## 6. Template Method (Шаблонный метод)

**Файл:** [app/patterns/template_method/delivery_process.py](../app/patterns/template_method/delivery_process.py)  
**Категория:** Поведенческий

### Что делает
Определяет скелет алгоритма обработки заказа в базовом классе, откладывая реализацию отдельных шагов в подклассы. Подклассы переопределяют конкретные шаги, не меняя структуру алгоритма.

### Как реализован
`BaseDeliveryProcess.execute()` — шаблонный метод, вызывающий по порядку:

1. `validate_order(order)` — абстрактный, реализован в каждом подклассе  
2. `calculate_price(order)` — конкретный, использует Strategy  
3. `process_payment(order)` — абстрактный  
4. `assign_courier(order)` — абстрактный  
5. `notify_client(order)` — конкретный, пишет в Logger

Три подкласса: `StandardDelivery`, `ExpressDelivery`, `EconomyDelivery`.

### Роль в системе
Демо `/demo/template-method/` запускает выбранный процесс и показывает пошаговый журнал из Logger. Процесс создаёт реальный заказ, платёж и назначает курьера.

---

## 7. Observer (Наблюдатель)

**Файл:** [app/patterns/observer/order_observer.py](../app/patterns/observer/order_observer.py)  
**Категория:** Поведенческий

### Что делает
Определяет зависимость «один ко многим»: при возникновении события в субъекте все зарегистрированные наблюдатели автоматически получают уведомление.

### Как реализован
`OrderSubject` хранит список `OrderObserver` и вызывает `update(order, event)` у каждого при `notify()`. Три конкретных наблюдателя:

- `ClientNotifier` — формирует уведомление для клиента (его имя + заказ)  
- `CourierNotifier` — формирует уведомление для курьера  
- `LoggerObserver` — записывает событие в собственный лог

Наблюдателей можно добавлять и отключать во время работы (`attach` / `detach`).

### Роль в системе
На демо `/demo/observer/` пользователь выбирает заказ, событие и набор наблюдателей. Фасад `DeliverySystemFacade` также автоматически подключает всех трёх наблюдателей при создании заказа. Адаптер (см. ниже) добавляет в ту же схему внешние сервисы.

---

## 8. Proxy (Заместитель)

**Файл:** [app/patterns/proxy/order_proxy.py](../app/patterns/proxy/order_proxy.py)  
**Категория:** Структурный

### Что делает
Предоставляет объект-заместитель, контролирующий доступ к реальному объекту `RealOrderService`. Заместитель реализует тот же интерфейс и проверяет права роли перед делегированием.

### Как реализован
`OrderServiceProxy` реализует `OrderServiceInterface` (три метода: `get_order`, `update_status`, `cancel_order`). Перед каждым вызовом проверяет матрицу прав:

| Роль    | Просмотр | Изменить статус | Отменить |
|---------|:--------:|:---------------:|:--------:|
| admin   | +        | +               | +        |
| courier | +        | +               | -        |
| client  | +        | -               | +        |
| guest   | +        | -               | -        |

Прокси ведёт `access_log` всех запросов.

### Роль в системе
Демо `/demo/proxy/` позволяет выбрать роль и действие, наглядно показывая разрешение или отказ в доступе.

---

## 9. Command (Команда)

**Файл:** [app/patterns/command/order_command.py](../app/patterns/command/order_command.py)  
**Категория:** Поведенческий

### Что делает
Инкапсулирует запрос как объект, что позволяет хранить историю операций и отменять их (`undo`).

### Как реализован
Абстрактный класс `Command` задаёт методы `execute()`, `undo()`, `description()`. Три конкретные команды:

- `NextStateCommand` — переход к следующему статусу, undo возвращает предыдущий  
- `CancelOrderCommand` — отмена заказа с возможностью undo  
- `AssignCourierCommand` — назначение курьера, undo убирает назначение

`CommandHistory` — стек выполненных команд с методами `execute(cmd)` и `undo()`.

### Роль в системе
Переходы статусов в карточке заказа (`order_next_state`, `order_cancel`) могут быть реализованы через команды. На демо `/demo/command/` пользователь выполняет команды и откатывает последнюю через кнопку «Undo». Фасад использует `CommandHistory` при создании заказа.

---

## 10. Adapter (Адаптер)

**Файл:** [app/patterns/adapter/notification_adapter.py](../app/patterns/adapter/notification_adapter.py)  
**Внешний модуль:** [app/modules/external_notify.py](../app/modules/external_notify.py)  
**Категория:** Структурный

### Что делает
Позволяет объектам с несовместимыми интерфейсами работать вместе. Адаптер оборачивает внешний сервис, реализуя интерфейс, ожидаемый системой.

### Как реализован
Внешний модуль `app/modules/external_notify.py` содержит два сторонних сервиса со своими методами:

- `ExternalSMSGateway.send_message(phone, text)` — отправляет SMS  
- `ExternalEmailService.dispatch(to, subject, body)` — отправляет письмо

Оба несовместимы с `OrderObserver.update(order, event)`. Два адаптера решают проблему:

- `SMSGatewayAdapter(OrderObserver)` — в `update()` извлекает телефон и вызывает `send_message()`  
- `EmailServiceAdapter(OrderObserver)` — в `update()` извлекает email и вызывает `dispatch()`

Адаптеры подключаются к `OrderSubject` так же, как и обычные наблюдатели.

### Роль в системе
Демо `/demo/adapter/` подключает внешние сервисы к системе уведомлений, не меняя ни `OrderSubject`, ни внешние сервисы. Это иллюстрирует принцип открытости/закрытости.

---

## 11. Facade (Фасад)

**Файл:** [app/patterns/facade/delivery_facade.py](../app/patterns/facade/delivery_facade.py)  
**Категория:** Структурный

### Что делает
Предоставляет упрощённый интерфейс к набору сложных подсистем. Клиент делает один вызов — фасад координирует несколько паттернов внутри.

### Как реализован
`DeliverySystemFacade.create_order()` выполняет полный цикл:

1. Создаёт заказ, платёж и трекинг через **Abstract Factory**  
2. Применяет выбранные **Decorator** к цене  
3. Подключает наблюдателей и отправляет событие через **Observer**  
4. Записывает переход статуса через **Command** в `CommandHistory`  
5. Логирует каждый шаг через **Singleton Logger**

Метод `get_order_summary(order_id)` возвращает краткую сводку по заказу без знания деталей ORM.

### Роль в системе
Демо `/demo/facade/` показывает, как клиентский код взаимодействует только с фасадом, не зная о фабриках, декораторах и командах. Соответствует требованию Этапа 4 — доступ к приложению через Фасад.

---

## 12. Composite (Компоновщик)

**Файл:** [app/patterns/composite/order_composite.py](../app/patterns/composite/order_composite.py)  
**Категория:** Структурный

### Что делает
Компонует объекты в древовидные структуры для представления иерархий часть–целое. Клиент работает с отдельными заказами и группами единообразно.

### Как реализован
Абстрактный класс `OrderComponent` объявляет `get_total_price()`, `get_count()`, `display()`. Два конкретных класса:

- `OrderLeaf` — одиночный заказ (лист дерева). Возвращает свою цену и 1.  
- `OrderGroup` — группа, хранит список `_children: list[OrderComponent]`. Агрегирует `get_total_price()` и `get_count()` рекурсивно.

Функция `build_tree_from_db()` строит дерево из БД: корень → группы по тарифу → группы по статусу → листья.

### Роль в системе
Демо `/demo/composite/` отображает всю иерархию заказов с агрегированными суммами на каждом уровне. Iterator обходит то же дерево.

---

## 13. Iterator (Итератор)

**Файл:** [app/patterns/iterator/order_iterator.py](../app/patterns/iterator/order_iterator.py)  
**Категория:** Поведенческий

### Что делает
Предоставляет способ последовательного обхода элементов составного объекта, не раскрывая его внутреннего представления.

### Как реализован
`OrderIterator` принимает корень дерева `OrderComponent`, рекурсивно собирает все листья (обход в глубину, DFS) и предоставляет интерфейс `has_next()` / `next()`. Реализует протокол `__iter__` / `__next__` для совместимости с циклом `for`.

`FilterIterator` — надстройка над `OrderIterator`: принимает итератор и строку статуса, при обходе возвращает только листья с нужным статусом. Демонстрирует компоновку итераторов.

### Роль в системе
На демо `/demo/composite/` пользователь фильтрует заказы по статусу через GET-параметр `status_filter`. `OrderIterator` проходит по всему дереву, `FilterIterator` отбирает нужные. Это соответствует требованию Этапа 4 — перебор элементов иерархии через Iterator.

---

## 14. A* / Dijkstra (Математическая модель)

**Файл:** [app/math_models/shortest_path.py](../app/math_models/shortest_path.py)  
**Демо-страница:** `/demo/astar/`

### Что делает
Находит кратчайший путь между двумя узлами графа маршрутов доставки.

### Как реализован
`ShortestPathFinder` хранит граф как `dict[str, list[(str, float)]]`. Метод `load_from_db()` загружает рёбра из модели `RouteGraph` (Django ORM). Алгоритм `find_shortest_path(start, end)` использует приоритетную очередь (`heapq`) и возвращает пару `(path: list[str], distance: float)`.

Граф хранится в таблице `RouteGraph` (поля: `from_node`, `to_node`, `distance`). Рёбра двунаправленные — каждая пара записана дважды.

### Роль в системе
Используется для оптимального маршрута при назначении курьера. Демо `/demo/astar/` позволяет выбрать начальный и конечный узел и увидеть найденный путь с суммарным расстоянием.

---

## Взаимодействие паттернов

```
DeliverySystemFacade
├── AbstractFactory  (создаёт Order + Payment + Tracking)
├── Decorator        (модифицирует цену)
├── Observer         (уведомляет подписчиков)
│   ├── ClientNotifier
│   ├── CourierNotifier
│   ├── LoggerObserver
│   ├── SMSGatewayAdapter  ← Adapter (внешний ExternalSMSGateway)
│   └── EmailServiceAdapter ← Adapter (внешний ExternalEmailService)
├── Command          (NextStateCommand → CommandHistory)
└── Singleton Logger (логирует все шаги)

Order (модель)
├── State   (жизненный цикл: New → Delivered / Cancelled)
└── Strategy (расчёт цены по тарифу)

TemplateMethod (BaseDeliveryProcess)
├── Strategy (calculate_price)
└── Singleton Logger

Composite (OrderGroup / OrderLeaf)
└── Iterator (OrderIterator / FilterIterator)

Proxy (OrderServiceProxy)
└── RealOrderService (доступ с проверкой прав по роли)
```
