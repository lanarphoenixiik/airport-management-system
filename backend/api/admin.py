from django.contrib import admin
from .models import (
    Airline, Airport, Aircraft, AirportResource,
    Flight, Passenger, Ticket, ServiceRequest, AuditLog
)

@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    list_display = ['name', 'iata_code', 'icao_code', 'country']
    search_fields = ['name', 'iata_code']

@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ['name', 'iata_code', 'city', 'country']
    search_fields = ['name', 'iata_code', 'city']

@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    list_display = ['registration', 'model', 'capacity', 'airline']
    search_fields = ['registration', 'model']
    list_filter = ['airline']

@admin.register(AirportResource)
class AirportResourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'terminal', 'status']
    list_filter = ['type', 'status']
    search_fields = ['name']

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ['flight_number', 'airline', 'scheduled_departure', 'status']
    list_filter = ['status', 'airline']
    search_fields = ['flight_number']
    date_hierarchy = 'scheduled_departure'

@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'passport_number', 'email', 'phone']
    search_fields = ['last_name', 'first_name', 'passport_number', 'email']

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'passenger', 'flight', 'status', 'class_type']
    list_filter = ['status', 'class_type']
    search_fields = ['ticket_number']

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'status', 'created_by', 'assigned_to']
    list_filter = ['status', 'priority']
    search_fields = ['title']

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'entity', 'created_at']
    list_filter = ['action', 'entity']
    date_hierarchy = 'created_at'