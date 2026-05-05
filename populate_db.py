import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from app.models import User, Client, Courier, Order, Payment, Tracking, Review, RouteGraph
from decimal import Decimal

def populate():
    print("Заполнение базы данных...")

    users = []
    for i in range(1, 6):
        user = User.objects.create_user(
            username=f"client{i}",
            password=f"pass{i}",
            email=f"client{i}@example.com"
        )
        users.append(user)
        Client.objects.create(user=user)
        print(f"Создан клиент: client{i}")

    couriers = []
    for i in range(1, 4):
        user = User.objects.create_user(
            username=f"courier{i}",
            password=f"pass{i}",
            email=f"courier{i}@example.com"
        )
        courier = Courier.objects.create(
            user=user,
            vehicle="Авто" if i == 1 else "Велосипед",
            rating=Decimal(f"{4.5 + i * 0.2}")
        )
        couriers.append(courier)
        print(f"Создан курьер: courier{i}")

    tariffs = ['economy', 'standard', 'express']
    statuses = ['new', 'payment_pending', 'courier_assigned', 'in_delivery', 'delivered']
    
    for i in range(1, 11):
        order = Order.objects.create(
            user=users[i % len(users)],
            courier=couriers[i % len(couriers)] if i % 2 == 0 else None,
            pickup_address=f"Улица {i}, дом {i}",
            delivery_address=f"Проспект {i}, дом {i*10}",
            tariff=tariffs[i % 3],
            price=Decimal(i * 500),
            status=statuses[i % len(statuses)]
        )
        
        Payment.objects.create(
            order=order,
            amount=order.price,
            method="card" if i % 2 == 0 else "cash"
        )
        
        Tracking.objects.create(
            order=order,
            status=order.get_status_display()
        )
        
        print(f"Создан заказ #{order.id}")

    routes = [
        ("А", "Б", 5), ("А", "В", 10), ("Б", "В", 3),
        ("Б", "Г", 8), ("В", "Г", 4), ("Г", "Д", 6),
        ("В", "Д", 12), ("Д", "Е", 7), ("Г", "Е", 9),
    ]
    
    for from_node, to_node, distance in routes:
        RouteGraph.objects.get_or_create(
            from_node=from_node,
            to_node=to_node,
            defaults={'distance': distance}
        )
    
    print(f"Создано {RouteGraph.objects.count()} маршрутов")
    print("Готово!")

if __name__ == "__main__":
    populate()