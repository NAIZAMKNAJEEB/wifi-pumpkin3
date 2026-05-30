from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('attack/start/', views.start_attack, name='start_attack'),
    path('attack/stop/', views.stop_attack, name='stop_attack'),
    path('logs/', views.get_logs, name='get_logs'),
    path('settings/', views.settings_view, name='settings'),
    path('api/scan/', views.scan_networks, name='scan_networks'),
    path('api/clients/', views.get_clients, name='get_clients'),
    path('api/deauth/', views.deauth_target, name='deauth_target'),
]
