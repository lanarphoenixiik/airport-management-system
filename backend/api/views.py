"""
Представления (Viewsets) для REST API
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import date
from django.db import models as django_models

from .models import (
    Airline, Airport, Aircraft, AirportResource,
    Flight, Passenger, Ticket, ServiceRequest, AuditLog
)
from .serializers import (
    AirlineSerializer, AirportSerializer, AircraftSerializer,
    AirportResourceSerializer, FlightListSerializer, FlightDetailSerializer,
    FlightCreateUpdateSerializer, PassengerSerializer, PassengerCreateSerializer,
    TicketSerializer, TicketCreateSerializer, ServiceRequestSerializer,
    ServiceRequestCreateSerializer, AuditLogSerializer
)


class AirlineViewSet(viewsets.ModelViewSet):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'iata_code']


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'iata_code', 'city', 'country']


class AircraftViewSet(viewsets.ModelViewSet):
    queryset = Aircraft.objects.all()
    serializer_class = AircraftSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['registration', 'model']


class AirportResourceViewSet(viewsets.ModelViewSet):
    queryset = AirportResource.objects.all()
    serializer_class = AirportResourceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['type', 'terminal', 'status']
    search_fields = ['name', 'description']


class FlightViewSet(viewsets.ModelViewSet):
    """Управление рейсами"""
    queryset = Flight.objects.all().select_related(
        'airline', 'aircraft', 'departure_airport', 'arrival_airport',
        'gate', 'check_in_counter', 'stand'
    )
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'airline', 'departure_airport', 'arrival_airport']
    search_fields = ['flight_number']
    ordering_fields = ['scheduled_departure', 'scheduled_arrival']
    ordering = ['scheduled_departure']

    def get_serializer_class(self):
        if self.action == 'list':
            return FlightListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return FlightCreateUpdateSerializer
        return FlightDetailSerializer

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Получение рейсов на сегодня"""
        today = date.today()
        flights = self.get_queryset().filter(scheduled_departure__date=today)
        serializer = FlightListSerializer(flights, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """Получение рейсов по статусу"""
        status_param = request.query_params.get('status', None)
        if status_param:
            flights = self.get_queryset().filter(status=status_param)
            serializer = FlightListSerializer(flights, many=True)
            return Response(serializer.data)
        return Response({'error': 'Не указан параметр status'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def assign_resources(self, request, pk=None):
        """Ручное назначение ресурсов рейсу"""
        flight = self.get_object()
        gate_id = request.data.get('gate_id')
        counter_id = request.data.get('check_in_counter_id')
        stand_id = request.data.get('stand_id')

        if gate_id:
            gate = AirportResource.objects.filter(id=gate_id, type='gate', status='available').first()
            if gate:
                gate.status = 'occupied'
                gate.save()
                flight.gate = gate
        if counter_id:
            counter = AirportResource.objects.filter(id=counter_id, type='check_in_counter', status='available').first()
            if counter:
                counter.status = 'occupied'
                counter.save()
                flight.check_in_counter = counter
        if stand_id:
            stand = AirportResource.objects.filter(id=stand_id, type='stand', status='available').first()
            if stand:
                stand.status = 'occupied'
                stand.save()
                flight.stand = stand

        flight.save()
        serializer = FlightDetailSerializer(flight)
        return Response(serializer.data)


class PassengerViewSet(viewsets.ModelViewSet):
    """Управление пассажирами"""
    queryset = Passenger.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'passport_number', 'email', 'phone']

    def get_serializer_class(self):
        if self.action == 'create':
            return PassengerCreateSerializer
        return PassengerSerializer

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Поиск пассажира по различным критериям"""
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Не указан параметр q'}, status=status.HTTP_400_BAD_REQUEST)

        passengers = Passenger.objects.filter(
            django_models.Q(first_name__icontains=query) |
            django_models.Q(last_name__icontains=query) |
            django_models.Q(passport_number__icontains=query) |
            django_models.Q(email__icontains=query) |
            django_models.Q(phone__icontains=query)
        )
        serializer = PassengerSerializer(passengers, many=True)
        return Response(serializer.data)


class TicketViewSet(viewsets.ModelViewSet):
    """Управление билетами"""
    queryset = Ticket.objects.all().select_related('passenger', 'flight')
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['status', 'class_type', 'flight']
    search_fields = ['ticket_number']

    def get_serializer_class(self):
        if self.action == 'create':
            return TicketCreateSerializer
        return TicketSerializer

    @action(detail=False, methods=['get'])
    def by_flight(self, request):
        """Получение билетов по рейсу"""
        flight_id = request.query_params.get('flight_id', None)
        if not flight_id:
            return Response({'error': 'Не указан параметр flight_id'}, status=status.HTTP_400_BAD_REQUEST)
        tickets = self.get_queryset().filter(flight_id=flight_id)
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_passenger(self, request):
        """Получение билетов по пассажиру"""
        passenger_id = request.query_params.get('passenger_id', None)
        if not passenger_id:
            return Response({'error': 'Не указан параметр passenger_id'}, status=status.HTTP_400_BAD_REQUEST)
        tickets = self.get_queryset().filter(passenger_id=passenger_id)
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        """Регистрация пассажира"""
        ticket = self.get_object()
        if ticket.status != 'booked':
            return Response({'error': 'Билет уже зарегистрирован'}, status=status.HTTP_400_BAD_REQUEST)

        ticket.status = 'checked_in'
        seat = request.data.get('seat_number')
        if seat:
            ticket.seat_number = seat
        ticket.save()

        serializer = TicketSerializer(ticket)
        return Response(serializer.data)


class ServiceRequestViewSet(viewsets.ModelViewSet):
    """Управление заявками на обслуживание"""
    queryset = ServiceRequest.objects.all().select_related('resource', 'created_by', 'assigned_to')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'assigned_to', 'resource']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'planned_completion_date']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return ServiceRequestCreateSerializer
        return ServiceRequestSerializer

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Назначение исполнителя на заявку"""
        request_obj = self.get_object()
        assigned_to_id = request.data.get('assigned_to_id')
        if not assigned_to_id:
            return Response({'error': 'Не указан assigned_to_id'}, status=status.HTTP_400_BAD_REQUEST)

        from django.contrib.auth.models import User
        user = User.objects.filter(id=assigned_to_id).first()
        if not user:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

        request_obj.assigned_to = user
        request_obj.status = 'in_progress'
        request_obj.save()

        serializer = ServiceRequestSerializer(request_obj)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Завершение заявки"""
        request_obj = self.get_object()
        request_obj.status = 'completed'
        request_obj.actual_completion_date = timezone.now()
        request_obj.save()

        serializer = ServiceRequestSerializer(request_obj)
        return Response(serializer.data)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Просмотр журнала аудита (только чтение)"""
    queryset = AuditLog.objects.all().select_related('user')
    serializer_class = AuditLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'action', 'entity']
    ordering = ['-created_at']