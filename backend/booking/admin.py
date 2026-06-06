from django.contrib import admin
from .models import Booking, BookingFile, MenuItem, Notification, RestaurantTable


@admin.register(RestaurantTable)
class RestaurantTableAdmin(admin.ModelAdmin):
    list_display = ('number', 'capacity', 'is_active')
    search_fields = ('number', 'description')
    list_filter = ('is_active',)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available')
    search_fields = ('name', 'description', 'category')
    list_filter = ('category', 'is_available')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'table', 'date', 'time_start', 'time_end', 'status')
    list_filter = ('status', 'date')
    search_fields = ('user__username', 'user__email', 'table__number')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'delivery_channel', 'email_status', 'is_read', 'created_at')
    list_filter = ('delivery_channel', 'email_status', 'is_read')


@admin.register(BookingFile)
class BookingFileAdmin(admin.ModelAdmin):
    list_display = ('booking', 'file_type', 'created_at')
