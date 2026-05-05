import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from app.models import User, Client, Courier, Order, Payment, Tracking, Review, RouteGraph
from decimal import Decimal

def populate():
    print("Заполнение базы данных...")
    
    # Очистка старых данных
    print("Очистка старых данных...")
    Order.objects.all().delete()
    Payment.objects.all().delete()
    Tracking.objects.all().delete()
    Review.objects.all().delete()
    RouteGraph.objects.all().delete()
    Client.objects.all().delete()
    Courier.objects.all().delete()
    User.objects.filter(username__startswith='client').delete()
    User.objects.filter(username__startswith='courier').delete()

    # Создание пользователей-клиентов
    users = []
    for i in range(1, 11):
        user = User.objects.create_user(
            username=f"client{i}",
            password=f"pass{i}",
            email=f"client{i}@example.com",
            phone=f"+7-900-000-00-{i:02d}",
            address=f"Улица Клиентская, д.{i}"
        )
        users.append(user)
        Client.objects.create(user=user)
        print(f"✓ Создан клиент: client{i}")

    # Создание курьеров
    couriers = []
    vehicles = ["Авто", "Велосипед", "Мотоцикл", "Скутер"]
    for i in range(1, 8):
        user = User.objects.create_user(
            username=f"courier{i}",
            password=f"pass{i}",
            email=f"courier{i}@example.com",
            phone=f"+7-900-100-00-{i:02d}",
            address=f"Улица Курьерская, д.{i}"
        )
        courier = Courier.objects.create(
            user=user,
            vehicle=vehicles[i % len(vehicles)],
            rating=Decimal(f"{4.0 + (i * 0.15):.2f}"),
            is_available=True if i % 2 == 0 else False
        )
        couriers.append(courier)
        print(f"✓ Создан курьер: courier{i}")

    # Создание заказов (25+ записей)
    tariffs = ['economy', 'standard', 'express']
    statuses = ['new', 'payment_pending', 'courier_assigned', 'in_delivery', 'delivered']
    
    addresses_pickup = [
        "ул. Красная, д. 1", "пр. Мира, д. 5", "бул. Чистый, д. 10",
        "ул. Торговая, д. 3", "пр. Науки, д. 7", "ул. Парковая, д. 2",
        "ул. Центральная, д. 8", "пр. Победы, д. 4", "ул. Зелёная, д. 6",
        "ул. Новая, д. 9", "пр. Свободы, д. 11", "ул. Лесная, д. 12",
    ]
    
    addresses_delivery = [
        "ул. Синяя, д. 20", "пр. Труда, д. 25", "бул. Цветной, д. 30",
        "ул. Рыночная, д. 15", "пр. Академическая, д. 35", "ул. Школьная, д. 18",
        "ул. Администрации, д. 22", "пр. Советская, д. 28", "ул. Сосновая, д. 24",
        "ул. Первая, д. 19", "пр. Независимости, д. 32", "ул. Береговая, д. 21",
    ]
    
    prices_base = {
        'economy': Decimal(500),
        'standard': Decimal(800),
        'express': Decimal(1500),
    }
    
    print("\nСоздание заказов:")
    for i in range(1, 26):
        tariff = tariffs[(i - 1) % len(tariffs)]
        status = statuses[(i - 1) % len(statuses)]
        
        data = {
            "user": users[(i - 1) % len(users)],
            "pickup_address": addresses_pickup[(i - 1) % len(addresses_pickup)],
            "delivery_address": addresses_delivery[(i - 1) % len(addresses_delivery)],
            "tariff": tariff,
            "price": prices_base[tariff] * (1 + Decimal(i % 5) / 10),
            "status": status,
        }
        
        # Назначаем курьера для некоторых заказов
        if status in ['courier_assigned', 'in_delivery', 'delivered']:
            data["courier"] = couriers[i % len(couriers)]

        order = Order.objects.create(**data)
        
        # Создание платежа
        Payment.objects.create(
            order=order,
            amount=order.price,
            method=["card", "cash", "instant"][i % 3]
        )
        
        # Создание трекинга
        Tracking.objects.create(
            order=order,
            status=order.get_status_display()
        )
        
        # Создание рецензии для доставленных заказов
        if status == 'delivered':
            Review.objects.create(
                order=order,
                rating=3 + (i % 3)
            )
        
        print(f"✓ Заказ #{order.id}: {tariff} - {status}")

    # Создание маршрутов для A*
    routes = [
        ("А", "Б", 5), ("А", "В", 10), ("Б", "В", 3),
        ("Б", "Г", 8), ("В", "Г", 4), ("Г", "Д", 6),
        ("В", "Д", 12), ("Д", "Е", 7), ("Г", "Е", 9),
        ("Е", "Ж", 5), ("Д", "Ж", 10), ("А", "Г", 15),
    ]
    
    print("\nСоздание маршрутов:")
    for from_node, to_node, distance in routes:
        route, created = RouteGraph.objects.get_or_create(
            from_node=from_node,
            to_node=to_node,
            defaults={'distance': distance}
        )
        if created:
            print(f"✓ Маршрут: {from_node} → {to_node} ({distance} км)")
    
    print(f"\n{'='*50}")
    print(f"✓ Создано пользователей: {User.objects.count()}")
    print(f"✓ Создано курьеров: {Courier.objects.count()}")
    print(f"✓ Создано заказов: {Order.objects.count()}")
    print(f"✓ Создано платежей: {Payment.objects.count()}")
    print(f"✓ Создано трекингов: {Tracking.objects.count()}")
    print(f"✓ Создано отзывов: {Review.objects.count()}")
    print(f"✓ Создано маршрутов: {RouteGraph.objects.count()}")
    print(f"{'='*50}")
    print("✓ Заполнение БД завершено!")

if __name__ == "__main__":
    populate()