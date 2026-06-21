"""
Маршруты для REST API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'airlines', views.AirlineViewSet)
router.register(r'airports', views.AirportViewSet)
router.register(r'aircraft', views.AircraftViewSet)
router.register(r'resources', views.AirportResourceViewSet)
router.register(r'flights', views.FlightViewSet)
router.register(r'passengers', views.PassengerViewSet)
router.register(r'tickets', views.TicketViewSet)
router.register(r'requests', views.ServiceRequestViewSet)
router.register(r'audit', views.AuditLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]