"""
Сериализаторы для REST API
"""

from rest_framework import serializers
from .models import (
    Airline, Airport, Aircraft, AirportResource,
    Flight, Passenger, Ticket, ServiceRequest, AuditLog
)


class AirlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airline
        fields = '__all__'


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = '__all__'


class AircraftSerializer(serializers.ModelSerializer):
    airline_name = serializers.CharField(source='airline.name', read_only=True)

    class Meta:
        model = Aircraft
        fields = ['id', 'registration', 'model', 'capacity', 'airline', 'airline_name']


class AirportResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirportResource
        fields = '__all__'


class FlightListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка рейсов (сокращённая информация)"""
    airline_name = serializers.CharField(source='airline.name', read_only=True)
    departure_airport_code = serializers.CharField(source='departure_airport.iata_code', read_only=True)
    arrival_airport_code = serializers.CharField(source='arrival_airport.iata_code', read_only=True)
    gate_name = serializers.CharField(source='gate.name', read_only=True, default=None)
    check_in_counter_name = serializers.CharField(source='check_in_counter.name', read_only=True, default=None)

    class Meta:
        model = Flight
        fields = [
            'id', 'flight_number', 'airline_name', 'departure_airport_code',
            'arrival_airport_code', 'scheduled_departure', 'scheduled_arrival',
            'status', 'gate_name', 'check_in_counter_name'
        ]


class FlightDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детальной информации о рейсе"""
    airline = AirlineSerializer(read_only=True)
    aircraft = AircraftSerializer(read_only=True)
    departure_airport = AirportSerializer(read_only=True)
    arrival_airport = AirportSerializer(read_only=True)
    gate = AirportResourceSerializer(read_only=True)
    check_in_counter = AirportResourceSerializer(read_only=True)
    stand = AirportResourceSerializer(read_only=True)

    class Meta:
        model = Flight
        fields = '__all__'


class FlightCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рейсов"""
    class Meta:
        model = Flight
        fields = [
            'flight_number', 'airline', 'aircraft', 'departure_airport',
            'arrival_airport', 'scheduled_departure', 'scheduled_arrival',
            'status', 'gate', 'check_in_counter', 'stand'
        ]


class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = ['id', 'first_name', 'last_name', 'middle_name', 'passport_number', 'email', 'phone', 'created_at']


class PassengerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = ['first_name', 'last_name', 'middle_name', 'passport_number', 'email', 'phone', 'password_hash']


class TicketSerializer(serializers.ModelSerializer):
    passenger_name = serializers.CharField(source='passenger.__str__', read_only=True)
    flight_info = serializers.CharField(source='flight.__str__', read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_number', 'passenger', 'passenger_name', 'flight',
            'flight_info', 'seat_number', 'class_type', 'price', 'status',
            'booking_date', 'ip_address'
        ]


class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            'ticket_number', 'passenger', 'flight', 'seat_number',
            'class_type', 'price', 'status', 'ip_address', 'payment_data'
        ]


class ServiceRequestSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True, default=None)
    resource_name = serializers.CharField(source='resource.name', read_only=True, default=None)

    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'title', 'description', 'priority', 'status', 'resource',
            'resource_name', 'created_by', 'created_by_name', 'assigned_to',
            'assigned_to_name', 'created_at', 'updated_at',
            'planned_completion_date', 'actual_completion_date'
        ]


class ServiceRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequest
        fields = [
            'title', 'description', 'priority', 'resource', 'assigned_to',
            'planned_completion_date'
        ]


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'user_name', 'action', 'entity', 'entity_id', 'data', 'ip_address', 'created_at']