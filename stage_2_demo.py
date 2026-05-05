import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from app.models import User, Order
from app.patterns.singleton.logger import Logger
from app.patterns.strategy.tariff_strategy import EconomyTariff, StandardTariff, ExpressTariff
from app.patterns.template_method.delivery_process import StandardDelivery, ExpressDelivery, EconomyDelivery
from app.patterns.abstract_factory.order_factory import StandardOrderFactory, ExpressOrderFactory, EconomyOrderFactory, PremiumOrderFactory
from app.patterns.decorator.order_decorator import InsuranceDecorator, PriorityDecorator, SMSNotifyDecorator, GiftWrapDecorator, FragileDecorator, SignatureRequiredDecorator
from app.math_models.shortest_path import ShortestPathFinder
from decimal import Decimal


def demo():
    print("\n" + "=" * 70)
    print("ДЕМОНСТРАЦИЯ ПАТТЕРНОВ ПРОЕКТИРОВАНИЯ - ЭТАП 2")
    print("=" * 70)

    try:
        # 1. SINGLETON PATTERN
        print("\n[1] ПАТТЕРН SINGLETON (Одиночка)")
        print("-" * 70)
        l1 = Logger()
        l2 = Logger()
        print(f"Logger создан дважды, но это один объект: {l1 is l2}")
        print(f"ID объекта l1: {id(l1)}")
        print(f"ID объекта l2: {id(l2)}")
        l1.log("Тестовое сообщение логгера")

        # 2. STRATEGY PATTERN
        print("\n[2] ПАТТЕРН STRATEGY (Стратегия)")
        print("-" * 70)
        print("Расчёт цены доставки на 10 км:")
        strategies = {
            'Эконом': EconomyTariff(),
            'Стандарт': StandardTariff(),
            'Экспресс': ExpressTariff(),
        }
        for name, strategy in strategies.items():
            price = strategy.calculate_price(10)
            print(f"  {name}: {price} руб.")

        # 3. TEMPLATE METHOD PATTERN
        print("\n[3] ПАТТЕРН TEMPLATE METHOD (Шаблонный метод)")
        print("-" * 70)
        user = User.objects.first()

        if user:
            print("Демонстрация StandardDelivery:")
            order = Order.objects.create(
                user=user,
                pickup_address="Ул. Красная, д. 1",
                delivery_address="Ул. Синяя, д. 20",
                tariff="standard",
                price=Decimal(0),
                status="new"
            )
            print(f"✓ Создан заказ #{order.id}")
            StandardDelivery().execute(order)

            print("\nДемонстрация ExpressDelivery:")
            order2 = Order.objects.create(
                user=user,
                pickup_address="Пр. Мира, д. 5",
                delivery_address="Пр. Труда, д. 25",
                tariff="express",
                price=Decimal(0),
                status="new"
            )
            print(f"✓ Создан заказ #{order2.id}")
            ExpressDelivery().execute(order2)

        # 4. ABSTRACT FACTORY PATTERN
        print("\n[4] ПАТТЕРН ABSTRACT FACTORY (Абстрактная фабрика)")
        print("-" * 70)

        if user:
            print("StandardOrderFactory:")
            sf = StandardOrderFactory()
            o1 = sf.create_order(
                user=user,
                pickup_address="Ул. Торговая, д. 3",
                delivery_address="Ул. Рыночная, д. 15",
                price=Decimal(4000)
            )
            payment1 = sf.create_payment(o1, o1.price)
            tracking1 = sf.create_tracking(o1)
            print(f"✓ Стандартный заказ #{o1.id}")
            print(f"  Платёж: {payment1.id} ({payment1.method})")
            print(f"  Трекинг: {tracking1.id} ({tracking1.status})")

            print("\nExpressOrderFactory:")
            ef = ExpressOrderFactory()
            o2 = ef.create_order(
                user=user,
                pickup_address="Бул. Чистый, д. 10",
                delivery_address="Бул. Цветной, д. 30"
            )
            payment2 = ef.create_payment(o2, o2.price)
            tracking2 = ef.create_tracking(o2)
            print(f"✓ Экспресс-заказ #{o2.id}")
            print(f"  Цена: {o2.price} руб.")
            print(f"  Платёж: {payment2.id} ({payment2.method})")
            print(f"  Трекинг: {tracking2.id} ({tracking2.status})")

            print("\nEconomyOrderFactory:")
            eco_f = EconomyOrderFactory()
            o3 = eco_f.create_order(
                user=user,
                pickup_address="Пр. Науки, д. 7",
                delivery_address="Пр. Академическая, д. 35"
            )
            eco_f.create_payment(o3, o3.price)
            eco_f.create_tracking(o3)
            print(f"✓ Экономный заказ #{o3.id} ({o3.price} руб.)")

        # 5. DECORATOR PATTERN
        print("\n[5] ПАТТЕРН DECORATOR (Декоратор)")
        print("-" * 70)

        if user:
            o4 = Order.objects.create(
                user=user,
                pickup_address="Ул. Парковая, д. 2",
                delivery_address="Ул. Школьная, д. 18",
                tariff="standard",
                price=Decimal(5000),
                status="new"
            )

            print(f"Базовая цена заказа #{o4.id}: {o4.price} руб.")
            print("\nДобавление услуг через декораторы:")
            
            print(f"  + Страховка: {InsuranceDecorator(o4).get_price()} руб.")
            print(f"  + Приоритет: {PriorityDecorator(o4).get_price()} руб.")
            print(f"  + SMS-уведомления: {SMSNotifyDecorator(o4).get_price()} руб.")
            print(f"  + Подарочная упаковка: {GiftWrapDecorator(o4).get_price()} руб.")
            print(f"  + Хрупкий товар: {FragileDecorator(o4).get_price()} руб.")
            print(f"  + Требуется подпись: {SignatureRequiredDecorator(o4).get_price()} руб.")

            # Комбинация декораторов
            print("\nКомбинация декораторов (страховка + приоритет + SMS):")
            decorated = SMSNotifyDecorator(
                PriorityDecorator(
                    InsuranceDecorator(o4)
                )
            )
            print(f"  Итоговая цена: {decorated.get_price()} руб.")
            print(f"  Описание: {decorated.get_description()}")

        # 6. A* MATHEMATICAL MODEL
        print("\n[6] МАТЕМАТИЧЕСКАЯ МОДЕЛЬ A* (Поиск кратчайшего пути)")
        print("-" * 70)

        pf = ShortestPathFinder()
        
        # Загружаем граф из БД или создаём вручную
        edges = [
            ("А", "Б", 5), ("Б", "В", 3), ("А", "В", 10),
            ("В", "Г", 4), ("Б", "Г", 8), ("Г", "Д", 6),
            ("В", "Д", 12), ("Д", "Е", 7), ("Г", "Е", 9),
        ]
        
        for from_node, to_node, distance in edges:
            pf.add_edge(from_node, to_node, distance)
        
        print("Граф маршрутов создан")
        print("Примеры поиска кратчайшего пути:")
        
        test_paths = [
            ("А", "Г"),
            ("А", "Е"),
            ("Б", "Е"),
        ]
        
        for start, end in test_paths:
            path, distance = pf.find_shortest_path(start, end)
            if path:
                path_str = " → ".join(path)
                print(f"  {start} → {end}: {path_str} (расстояние: {distance} км)")
            else:
                print(f"  {start} → {end}: Пути не найдено")

        # ИТОГИ
        print("\n" + "=" * 70)
        print("СТАТИСТИКА БД")
        print("=" * 70)
        from app.models import Client, Courier, Payment, Tracking, Review, RouteGraph
        print(f"✓ Пользователей: {User.objects.count()}")
        print(f"✓ Клиентов: {Client.objects.count()}")
        print(f"✓ Курьеров: {Courier.objects.count()}")
        print(f"✓ Заказов: {Order.objects.count()}")
        print(f"✓ Платежей: {Payment.objects.count()}")
        print(f"✓ Трекингов: {Tracking.objects.count()}")
        print(f"✓ Отзывов: {Review.objects.count()}")
        print(f"✓ Маршрутов: {RouteGraph.objects.count()}")

        print("\n" + "=" * 70)
        print("✓ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ ОШИБКА: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    demo()