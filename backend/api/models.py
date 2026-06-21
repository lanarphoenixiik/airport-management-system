"""
Модели базы данных для информационной системы управления аэровокзалом
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Airline(models.Model):
    """Авиакомпания"""
    name = models.CharField(max_length=100, verbose_name="Название")
    iata_code = models.CharField(max_length=2, verbose_name="Код IATA", blank=True)
    icao_code = models.CharField(max_length=3, verbose_name="Код ICAO", blank=True)
    country = models.CharField(max_length=50, verbose_name="Страна", blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Авиакомпания"
        verbose_name_plural = "Авиакомпании"


class Airport(models.Model):
    """Аэропорт"""
    name = models.CharField(max_length=100, verbose_name="Название")
    iata_code = models.CharField(max_length=3, verbose_name="Код IATA")
    icao_code = models.CharField(max_length=4, verbose_name="Код ICAO", blank=True)
    city = models.CharField(max_length=50, verbose_name="Город")
    country = models.CharField(max_length=50, verbose_name="Страна")

    def __str__(self):
        return f"{self.name} ({self.iata_code})"

    class Meta:
        verbose_name = "Аэропорт"
        verbose_name_plural = "Аэропорты"


class Aircraft(models.Model):
    """Воздушное судно"""
    registration = models.CharField(max_length=10, verbose_name="Регистрационный номер")
    model = models.CharField(max_length=50, verbose_name="Модель")
    capacity = models.IntegerField(verbose_name="Пассажировместимость")
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name='aircrafts', verbose_name="Авиакомпания")

    def __str__(self):
        return f"{self.model} ({self.registration})"

    class Meta:
        verbose_name = "Воздушное судно"
        verbose_name_plural = "Воздушные суда"


class AirportResource(models.Model):
    """Ресурс аэропорта (стойка, выход, стоянка)"""
    RESOURCE_TYPES = [
        ('check_in_counter', 'Стойка регистрации'),
        ('gate', 'Выход на посадку'),
        ('stand', 'Место стоянки'),
        ('vehicle', 'Спецтехника'),
    ]

    STATUS_CHOICES = [
        ('available', 'Доступен'),
        ('occupied', 'Занят'),
        ('maintenance', 'На обслуживании'),
        ('unavailable', 'Недоступен'),
    ]

    name = models.CharField(max_length=100, verbose_name="Название")
    type = models.CharField(max_length=20, choices=RESOURCE_TYPES, verbose_name="Тип")
    terminal = models.CharField(max_length=10, verbose_name="Терминал", blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name="Статус")
    description = models.TextField(blank=True, verbose_name="Описание")

    def __str__(self):
        return f"{self.get_type_display()} - {self.name}"

    class Meta:
        verbose_name = "Ресурс аэропорта"
        verbose_name_plural = "Ресурсы аэропорта"


class Flight(models.Model):
    """Рейс"""
    STATUS_CHOICES = [
        ('scheduled', 'Запланирован'),
        ('check_in', 'Регистрация открыта'),
        ('boarding', 'Посадка'),
        ('departed', 'Вылетел'),
        ('arrived', 'Прибыл'),
        ('delayed', 'Задержан'),
        ('cancelled', 'Отменён'),
        ('waiting_for_resource', 'Ожидает назначения ресурсов'),
    ]

    flight_number = models.CharField(max_length=10, verbose_name="Номер рейса")
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name='flights', verbose_name="Авиакомпания")
    aircraft = models.ForeignKey(Aircraft, on_delete=models.SET_NULL, null=True, related_name='flights', verbose_name="Воздушное судно")
    departure_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='departures', verbose_name="Аэропорт отправления")
    arrival_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='arrivals', verbose_name="Аэропорт назначения")
    scheduled_departure = models.DateTimeField(verbose_name="Плановое время вылета")
    scheduled_arrival = models.DateTimeField(verbose_name="Плановое время прибытия")
    actual_departure = models.DateTimeField(null=True, blank=True, verbose_name="Фактическое время вылета")
    actual_arrival = models.DateTimeField(null=True, blank=True, verbose_name="Фактическое время прибытия")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='scheduled', verbose_name="Статус")
    gate = models.ForeignKey(AirportResource, on_delete=models.SET_NULL, null=True, blank=True, related_name='flights_as_gate', verbose_name="Выход на посадку", limit_choices_to={'type': 'gate'})
    check_in_counter = models.ForeignKey(AirportResource, on_delete=models.SET_NULL, null=True, blank=True, related_name='flights_as_counter', verbose_name="Стойка регистрации", limit_choices_to={'type': 'check_in_counter'})
    stand = models.ForeignKey(AirportResource, on_delete=models.SET_NULL, null=True, blank=True, related_name='flights_as_stand', verbose_name="Место стоянки", limit_choices_to={'type': 'stand'})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.flight_number} - {self.departure_airport.iata_code} → {self.arrival_airport.iata_code}"

    class Meta:
        verbose_name = "Рейс"
        verbose_name_plural = "Рейсы"
        ordering = ['scheduled_departure']


class Passenger(models.Model):
    """Пассажир"""
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    middle_name = models.CharField(max_length=50, blank=True, verbose_name="Отчество")
    passport_number = models.CharField(max_length=20, verbose_name="Номер паспорта")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    password_hash = models.CharField(max_length=255, verbose_name="Хэш пароля")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    class Meta:
        verbose_name = "Пассажир"
        verbose_name_plural = "Пассажиры"


class Ticket(models.Model):
    """Билет"""
    STATUS_CHOICES = [
        ('booked', 'Забронирован'),
        ('checked_in', 'Зарегистрирован'),
        ('boarded', 'Посажен на борт'),
        ('used', 'Использован'),
        ('cancelled', 'Отменён'),
    ]

    CLASS_CHOICES = [
        ('economy', 'Эконом'),
        ('business', 'Бизнес'),
        ('first', 'Первый'),
    ]

    ticket_number = models.CharField(max_length=20, unique=True, verbose_name="Номер билета")
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, related_name='tickets', verbose_name="Пассажир")
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='tickets', verbose_name="Рейс")
    seat_number = models.CharField(max_length=5, blank=True, verbose_name="Номер места")
    class_type = models.CharField(max_length=10, choices=CLASS_CHOICES, default='economy', verbose_name="Класс")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='booked', verbose_name="Статус")
    booking_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата бронирования")
    payment_data = models.JSONField(default=dict, verbose_name="Данные о платеже")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP-адрес")

    def __str__(self):
        return f"{self.ticket_number} - {self.passenger}"

    class Meta:
        verbose_name = "Билет"
        verbose_name_plural = "Билеты"


class ServiceRequest(models.Model):
    """Заявка на обслуживание"""
    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
        ('critical', 'Критический'),
    ]

    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('awaiting_approval', 'На согласовании'),
        ('completed', 'Выполнена'),
        ('rejected', 'Отклонена'),
    ]

    title = models.CharField(max_length=255, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name="Приоритет")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    resource = models.ForeignKey(AirportResource, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Оборудование")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_requests', verbose_name="Создал")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_requests', verbose_name="Исполнитель")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    planned_completion_date = models.DateTimeField(null=True, blank=True, verbose_name="Плановая дата завершения")
    actual_completion_date = models.DateTimeField(null=True, blank=True, verbose_name="Фактическая дата завершения")

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Заявка на обслуживание"
        verbose_name_plural = "Заявки на обслуживание"
        ordering = ['-created_at']


class AuditLog(models.Model):
    """Журнал аудита"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    action = models.CharField(max_length=50, verbose_name="Действие")
    entity = models.CharField(max_length=50, verbose_name="Сущность")
    entity_id = models.IntegerField(verbose_name="ID сущности")
    data = models.JSONField(default=dict, verbose_name="Данные")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP-адрес")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата")

    def __str__(self):
        return f"{self.user} - {self.action} - {self.entity} #{self.entity_id}"

    class Meta:
        verbose_name = "Журнал аудита"
        verbose_name_plural = "Журналы аудита"
        ordering = ['-created_at']