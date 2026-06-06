from django.conf import settings
from django.db import models


class RestaurantTable(models.Model):
    number = models.PositiveIntegerField(unique=True, verbose_name='Номер столика')
    capacity = models.PositiveIntegerField(verbose_name='Количество мест')
    description = models.CharField(max_length=255, blank=True, verbose_name='Описание')
    image = models.ImageField(upload_to='uploads/tables/', blank=True, null=True, verbose_name='Изображение')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        ordering = ['number']
        verbose_name = 'Столик'
        verbose_name_plural = 'Столики'

    def __str__(self):
        return f'Столик {self.number} ({self.capacity} мест)'


class MenuItem(models.Model):
    name = models.CharField(max_length=120, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Цена')
    category = models.CharField(max_length=80, blank=True, verbose_name='Категория')
    image = models.ImageField(upload_to='uploads/menu/', blank=True, null=True, verbose_name='Изображение')
    is_available = models.BooleanField(default=True, verbose_name='Доступно')

    class Meta:
        ordering = ['category', 'name']
        verbose_name = 'Блюдо меню'
        verbose_name_plural = 'Блюда меню'

    def __str__(self):
        return self.name


class Booking(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Ожидает подтверждения'),
        (STATUS_CONFIRMED, 'Подтверждено'),
        (STATUS_CANCELLED, 'Отменено'),
        (STATUS_COMPLETED, 'Завершено'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    table = models.ForeignKey(RestaurantTable, on_delete=models.PROTECT, related_name='bookings')
    date = models.DateField(verbose_name='Дата')
    time_start = models.TimeField(verbose_name='Время начала')
    time_end = models.TimeField(verbose_name='Время окончания')
    guests_count = models.PositiveIntegerField(default=1, verbose_name='Количество гостей')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    pdf_path = models.CharField(max_length=255, blank=True, verbose_name='PDF-подтверждение')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-time_start']
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'

    def __str__(self):
        return f'{self.user.username}: столик {self.table.number} {self.date} {self.time_start}'


class Notification(models.Model):
    CHANNEL_SITE = 'site'
    CHANNEL_EMAIL = 'email'
    CHANNEL_BOTH = 'site_email'
    CHANNEL_CHOICES = [
        (CHANNEL_SITE, 'Внутри сайта'),
        (CHANNEL_EMAIL, 'Email'),
        (CHANNEL_BOTH, 'Сайт и email'),
    ]

    EMAIL_NOT_SENT = 'not_sent'
    EMAIL_SENT = 'sent'
    EMAIL_ERROR = 'error'
    EMAIL_STATUS_CHOICES = [
        (EMAIL_NOT_SENT, 'Не отправлено'),
        (EMAIL_SENT, 'Отправлено'),
        (EMAIL_ERROR, 'Ошибка отправки'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    title = models.CharField(max_length=160)
    message = models.TextField()
    delivery_channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default=CHANNEL_BOTH)
    email_status = models.CharField(max_length=20, choices=EMAIL_STATUS_CHOICES, default=EMAIL_NOT_SENT)
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'

    def __str__(self):
        return self.title


class BookingFile(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='confirmations/')
    file_type = models.CharField(max_length=20, default='pdf')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Файл бронирования'
        verbose_name_plural = 'Файлы бронирования'
