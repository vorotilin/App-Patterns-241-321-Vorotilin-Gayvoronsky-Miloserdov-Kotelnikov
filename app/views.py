from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from decimal import Decimal

from app.models import User, Order, Courier, Payment, Tracking, RouteGraph
from app.patterns.singleton.logger import Logger
from app.patterns.strategy.tariff_strategy import EconomyTariff, StandardTariff, ExpressTariff
from app.patterns.template_method.delivery_process import StandardDelivery, ExpressDelivery, EconomyDelivery
from app.patterns.abstract_factory.order_factory import (
    StandardOrderFactory, ExpressOrderFactory,
    EconomyOrderFactory, PremiumOrderFactory
)
from app.patterns.decorator.order_decorator import (
    OrderDecorator, InsuranceDecorator, PriorityDecorator,
    SMSNotifyDecorator, GiftWrapDecorator, FragileDecorator,
    SignatureRequiredDecorator
)
from app.patterns.observer.order_observer import (
    OrderSubject, ClientNotifier, CourierNotifier, LoggerObserver
)
from app.patterns.proxy.order_proxy import OrderServiceProxy
from app.patterns.command.order_command import (
    NextStateCommand, CancelOrderCommand, AssignCourierCommand, CommandHistory
)
from app.math_models.shortest_path import ShortestPathFinder


# ── Главная ──────────────────────────────────────────────────────────────────

def home(request):
    from app.models import Client
    context = {
        'orders_count': Order.objects.count(),
        'couriers_count': Courier.objects.count(),
        'clients_count': Client.objects.count(),
        'payments_count': Payment.objects.count(),
    }
    return render(request, 'app/home.html', context)


# ── Список заказов ────────────────────────────────────────────────────────────

def orders_list(request):
    orders = Order.objects.select_related('user', 'courier').order_by('-id')
    return render(request, 'app/orders_list.html', {'orders': orders})


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    payments = order.payments.all()
    tracking = getattr(order, 'tracking', None)
    review = getattr(order, 'review', None)
    return render(request, 'app/order_detail.html', {
        'order': order,
        'payments': payments,
        'tracking': tracking,
        'review': review,
    })


@require_POST
def order_next_state(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    old_status = order.get_status_display()
    order.next_state()
    new_status = order.get_status_display()
    logger = Logger()
    logger.log(f"Заказ #{order.id}: {old_status} → {new_status}")
    return redirect('order_detail', order_id=order.id)


@require_POST
def order_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.cancel_order()
    logger = Logger()
    logger.log(f"Заказ #{order.id} отменён")
    return redirect('order_detail', order_id=order.id)


# ── SINGLETON ─────────────────────────────────────────────────────────────────

def demo_singleton(request):
    logger1 = Logger()
    logger2 = Logger()

    if request.method == 'POST':
        msg = request.POST.get('message', '').strip()
        if msg:
            logger1.log(msg)

    context = {
        'is_same': logger1 is logger2,
        'id1': id(logger1),
        'id2': id(logger2),
        'logs': logger1.get_logs(),
    }
    return render(request, 'app/demo_singleton.html', context)


@require_POST
def clear_logs(request):
    Logger().clear()
    return redirect('demo_singleton')


# ── STRATEGY ──────────────────────────────────────────────────────────────────

def demo_strategy(request):
    result = None
    distance = None
    tariff = None

    if request.method == 'POST':
        try:
            distance = float(request.POST.get('distance', 10))
            tariff = request.POST.get('tariff', 'standard')
            strategies = {
                'economy': EconomyTariff(),
                'standard': StandardTariff(),
                'express': ExpressTariff(),
            }
            strategy = strategies.get(tariff, StandardTariff())
            result = strategy.calculate_price(distance)
        except (ValueError, TypeError):
            pass

    # Таблица сравнения для заданного расстояния
    compare_distance = distance or 10
    compare = {
        'economy': EconomyTariff().calculate_price(compare_distance),
        'standard': StandardTariff().calculate_price(compare_distance),
        'express': ExpressTariff().calculate_price(compare_distance),
    }

    return render(request, 'app/demo_strategy.html', {
        'result': result,
        'distance': distance or compare_distance,
        'tariff': tariff,
        'compare': compare,
    })


# ── ABSTRACT FACTORY ──────────────────────────────────────────────────────────

def demo_factory(request):
    result = None
    error = None

    FACTORIES = {
        'standard': StandardOrderFactory,
        'express': ExpressOrderFactory,
        'economy': EconomyOrderFactory,
        'premium': PremiumOrderFactory,
    }

    if request.method == 'POST':
        factory_type = request.POST.get('factory_type', 'standard')
        pickup = request.POST.get('pickup_address', '').strip()
        delivery = request.POST.get('delivery_address', '').strip()

        if not pickup or not delivery:
            error = "Заполните адреса отправки и доставки"
        else:
            user = User.objects.first()
            if not user:
                error = "Нет пользователей в БД. Запустите populate_db.py"
            else:
                factory_cls = FACTORIES.get(factory_type, StandardOrderFactory)
                factory = factory_cls()
                order = factory.create_order(
                    user=user,
                    pickup_address=pickup,
                    delivery_address=delivery,
                )
                payment = factory.create_payment(order, order.price)
                tracking = factory.create_tracking(order)
                Logger().log(f"[AbstractFactory:{factory_type}] Заказ #{order.id} создан")
                result = {
                    'factory_type': factory_type,
                    'order': order,
                    'payment': payment,
                    'tracking': tracking,
                }

    return render(request, 'app/demo_factory.html', {
        'result': result,
        'error': error,
        'factory_choices': list(FACTORIES.keys()),
    })


# ── DECORATOR ─────────────────────────────────────────────────────────────────

def demo_decorator(request):
    orders = Order.objects.order_by('-id')[:10]
    result = None
    error = None

    DECORATOR_MAP = {
        'insurance': InsuranceDecorator,
        'priority': PriorityDecorator,
        'sms': SMSNotifyDecorator,
        'gift_wrap': GiftWrapDecorator,
        'fragile': FragileDecorator,
        'signature': SignatureRequiredDecorator,
    }

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        selected = request.POST.getlist('decorators')

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            error = "Заказ не найден"
        else:
            # Строим цепочку декораторов
            decorated = order
            applied = []
            for key in selected:
                decorator_cls = DECORATOR_MAP.get(key)
                if decorator_cls:
                    decorated = decorator_cls(decorated)
                    applied.append(key)

            if not applied:
                final_price = order.price
                description = f"Заказ #{order.id}"
            else:
                final_price = decorated.get_price()
                description = decorated.get_description()

            Logger().log(f"[Decorator] Заказ #{order.id}: {description} = {final_price} руб.")
            result = {
                'order': order,
                'applied': applied,
                'final_price': final_price,
                'description': description,
                'base_price': order.price,
                'diff': final_price - order.price,
            }

    return render(request, 'app/demo_decorator.html', {
        'orders': orders,
        'result': result,
        'error': error,
        'decorator_choices': list(DECORATOR_MAP.keys()),
    })


# ── STATE ─────────────────────────────────────────────────────────────────────

def demo_state(request):
    orders = Order.objects.select_related('user').order_by('-id')
    state_flow = ['new', 'payment_pending', 'courier_assigned', 'in_delivery', 'delivered']
    return render(request, 'app/demo_state.html', {
        'orders': orders,
        'state_flow': state_flow,
    })


# ── TEMPLATE METHOD ───────────────────────────────────────────────────────────

def demo_template(request):
    result = None
    error = None

    PROCESSES = {
        'standard': StandardDelivery,
        'express': ExpressDelivery,
        'economy': EconomyDelivery,
    }

    if request.method == 'POST':
        process_type = request.POST.get('process_type', 'standard')
        pickup = request.POST.get('pickup_address', '').strip()
        delivery_addr = request.POST.get('delivery_address', '').strip()

        if not pickup or not delivery_addr:
            error = "Заполните адреса"
        else:
            user = User.objects.first()
            if not user:
                error = "Нет пользователей в БД"
            else:
                logger = Logger()
                logger.clear()

                order = Order.objects.create(
                    user=user,
                    pickup_address=pickup,
                    delivery_address=delivery_addr,
                    tariff=process_type if process_type != 'standard' else 'standard',
                    price=Decimal(0),
                    status='new',
                )

                process_cls = PROCESSES.get(process_type, StandardDelivery)
                process = process_cls()
                try:
                    process.execute(order)
                    order.refresh_from_db()
                    result = {
                        'process_type': process_type,
                        'order': order,
                        'logs': list(logger.get_logs()),
                    }
                except Exception as e:
                    error = str(e)
                    order.delete()

    return render(request, 'app/demo_template.html', {
        'result': result,
        'error': error,
        'process_choices': ['standard', 'express', 'economy'],
    })


# ── A* (Dijkstra) ─────────────────────────────────────────────────────────────

def demo_astar(request):
    pf = ShortestPathFinder()
    pf.load_from_db()

    nodes = sorted(set(pf.graph.keys()))
    result = None
    error = None

    if request.method == 'POST':
        start = request.POST.get('start', '')
        end = request.POST.get('end', '')

        if start == end:
            error = "Начальная и конечная точки совпадают"
        elif start not in pf.graph or end not in pf.graph:
            error = "Выбранные узлы не найдены в графе"
        else:
            path, distance = pf.find_shortest_path(start, end)
            if path:
                result = {
                    'start': start,
                    'end': end,
                    'path': path,
                    'distance': distance,
                    'path_str': ' → '.join(path),
                }
            else:
                error = f"Пути от {start} до {end} не найдено"

    edges = RouteGraph.objects.all()

    return render(request, 'app/demo_astar.html', {
        'nodes': nodes,
        'edges': edges,
        'result': result,
        'error': error,
    })


# ── OBSERVER ──────────────────────────────────────────────────────────────────

def demo_observer(request):
    orders = Order.objects.select_related('user', 'courier').order_by('-id')[:10]
    result = None
    error = None

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        event = request.POST.get('event', '').strip()
        observers_selected = request.POST.getlist('observers')

        try:
            order = Order.objects.select_related('user', 'courier').get(id=order_id)
        except Order.DoesNotExist:
            error = "Заказ не найден"
        else:
            subject = OrderSubject()
            client_obs = ClientNotifier()
            courier_obs = CourierNotifier()
            logger_obs = LoggerObserver()

            obs_map = {
                'client': client_obs,
                'courier': courier_obs,
                'logger': logger_obs,
            }
            attached = []
            for key in observers_selected:
                if key in obs_map:
                    subject.attach(obs_map[key])
                    attached.append(key)

            subject.notify(order, event or "Событие по заказу")

            notifications = (
                client_obs.notifications
                + courier_obs.notifications
                + logger_obs.log
            )
            result = {
                'order': order,
                'event': event,
                'attached': attached,
                'notifications': notifications,
            }

    return render(request, 'app/demo_observer.html', {
        'orders': orders,
        'result': result,
        'error': error,
    })


# ── PROXY ─────────────────────────────────────────────────────────────────────

def demo_proxy(request):
    orders = Order.objects.select_related('user').order_by('-id')[:10]
    result = None
    error = None

    STATUS_CHOICES = ['new', 'payment_pending', 'courier_assigned', 'in_delivery', 'delivered', 'cancelled']
    ROLES = ['admin', 'courier', 'client', 'guest']

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        role = request.POST.get('role', 'guest')
        action = request.POST.get('action', 'get')
        new_status = request.POST.get('new_status', 'payment_pending')

        proxy = OrderServiceProxy()
        try:
            if action == 'update_status':
                order = proxy.update_status(int(order_id), new_status, role)
            elif action == 'cancel':
                order = proxy.cancel_order(int(order_id), role)
            else:
                order = proxy.get_order(int(order_id))
            result = {
                'order': order,
                'role': role,
                'action': action,
                'log': proxy.access_log,
                'granted': True,
            }
        except PermissionError as e:
            proxy_log = proxy.access_log
            result = {
                'role': role,
                'action': action,
                'log': proxy_log,
                'granted': False,
                'reason': str(e),
            }
        except Exception as e:
            error = str(e)

    return render(request, 'app/demo_proxy.html', {
        'orders': orders,
        'result': result,
        'error': error,
        'roles': ROLES,
        'status_choices': STATUS_CHOICES,
    })


# ── COMMAND ───────────────────────────────────────────────────────────────────

_command_history = CommandHistory()


def demo_command(request):
    orders = Order.objects.select_related('user', 'courier').order_by('-id')[:10]
    couriers = Courier.objects.select_related('user').filter(is_available=True)
    result = None
    error = None

    if request.method == 'POST':
        action = request.POST.get('action')
        order_id = request.POST.get('order_id')

        try:
            order = Order.objects.select_related('user', 'courier').get(id=order_id)
        except Order.DoesNotExist:
            error = "Заказ не найден"
            order = None

        if order and action == 'next_state':
            cmd = NextStateCommand(order)
            _command_history.execute(cmd)
            result = {'action': 'Переход к следующему статусу', 'order': order, 'cmd': cmd.description()}

        elif order and action == 'cancel':
            cmd = CancelOrderCommand(order)
            _command_history.execute(cmd)
            result = {'action': 'Отмена заказа', 'order': order, 'cmd': cmd.description()}

        elif order and action == 'assign_courier':
            courier_id = request.POST.get('courier_id')
            try:
                courier = Courier.objects.select_related('user').get(id=courier_id)
                cmd = AssignCourierCommand(order, courier)
                _command_history.execute(cmd)
                order.refresh_from_db()
                result = {'action': 'Назначение курьера', 'order': order, 'cmd': cmd.description()}
            except Courier.DoesNotExist:
                error = "Курьер не найден"

        elif action == 'undo':
            undone = _command_history.undo()
            if undone:
                result = {'action': 'Отмена команды (undo)', 'cmd': undone.description(), 'order': None}
            else:
                error = "История команд пуста"

    history = _command_history.get_history()

    return render(request, 'app/demo_command.html', {
        'orders': orders,
        'couriers': couriers,
        'result': result,
        'error': error,
        'history': [cmd.description() for cmd in history],
    })
