from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Booking, BookingFile, MenuItem, Notification, RestaurantTable
from .services import is_table_available


class UserSerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_admin']

    def get_is_admin(self, obj):
        return obj.is_staff or obj.is_superuser


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class RestaurantTableSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = RestaurantTable
        fields = ['id', 'number', 'capacity', 'description', 'image', 'image_url', 'is_active']
        read_only_fields = ['image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class MenuItemSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price', 'category', 'image', 'image_url', 'is_available']
        read_only_fields = ['image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class BookingFileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = BookingFile
        fields = ['id', 'file', 'file_url', 'file_type', 'created_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    table_info = RestaurantTableSerializer(source='table', read_only=True)
    files = BookingFileSerializer(many=True, read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'table', 'table_info', 'date', 'time_start', 'time_end',
            'guests_count', 'status', 'comment', 'pdf_path', 'files', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'status', 'pdf_path']

    def validate(self, attrs):
        table = attrs.get('table') or getattr(self.instance, 'table', None)
        date = attrs.get('date') or getattr(self.instance, 'date', None)
        time_start = attrs.get('time_start') or getattr(self.instance, 'time_start', None)
        time_end = attrs.get('time_end') or getattr(self.instance, 'time_end', None)
        guests_count = attrs.get('guests_count') or getattr(self.instance, 'guests_count', 1)
        if time_start and time_end and time_start >= time_end:
            raise serializers.ValidationError('Время окончания должно быть позже времени начала.')
        if table and guests_count and guests_count > table.capacity:
            raise serializers.ValidationError('Количество гостей превышает вместимость столика.')
        if table and date and time_start and time_end:
            exclude_id = self.instance.id if self.instance else None
            if not is_table_available(table, date, time_start, time_end, exclude_id):
                raise serializers.ValidationError('Столик занят на выбранное время.')
        return attrs


class BookingStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['status']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'booking', 'title', 'message', 'delivery_channel', 'email_status', 'is_read', 'sent_at', 'created_at']
        read_only_fields = ['delivery_channel', 'email_status', 'sent_at', 'created_at']
