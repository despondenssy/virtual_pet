from django.urls import path
from .views.command_views import ChargeEnergyAPIView, SpendEnergyAPIView
from .views.query_views import EnergyViewAPIView, EnergyHistoryAPIView

urlpatterns = [
    # Команды - POST
    path('commands/charge/', ChargeEnergyAPIView.as_view(), name='charge_energy'),
    path('commands/spend/', SpendEnergyAPIView.as_view(), name='spend_energy'),

    # Запросы - GET
    path('queries/energy/<str:pet_id>/', EnergyViewAPIView.as_view(), name='energy_view'),
    path('queries/history/<str:pet_id>/', EnergyHistoryAPIView.as_view(), name='energy_history'),
]