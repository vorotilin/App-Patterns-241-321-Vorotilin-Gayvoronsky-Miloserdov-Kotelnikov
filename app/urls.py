from django.urls import path
from app import views

urlpatterns = [
    path('', views.home, name='home'),

    # Orders
    path('orders/', views.orders_list, name='orders_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/next/', views.order_next_state, name='order_next_state'),
    path('orders/<int:order_id>/cancel/', views.order_cancel, name='order_cancel'),

    # Pattern demos
    path('demo/singleton/', views.demo_singleton, name='demo_singleton'),
    path('demo/singleton/clear/', views.clear_logs, name='clear_logs'),
    path('demo/strategy/', views.demo_strategy, name='demo_strategy'),
    path('demo/factory/', views.demo_factory, name='demo_factory'),
    path('demo/decorator/', views.demo_decorator, name='demo_decorator'),
    path('demo/state/', views.demo_state, name='demo_state'),
    path('demo/template-method/', views.demo_template, name='demo_template'),
    path('demo/astar/', views.demo_astar, name='demo_astar'),
    path('demo/observer/', views.demo_observer, name='demo_observer'),
    path('demo/proxy/', views.demo_proxy, name='demo_proxy'),
    path('demo/command/', views.demo_command, name='demo_command'),
    path('demo/adapter/', views.demo_adapter, name='demo_adapter'),
    path('demo/facade/', views.demo_facade, name='demo_facade'),
    path('demo/composite/', views.demo_composite, name='demo_composite'),
    path('demo/iterator/', views.demo_composite, name='demo_iterator'),
]
