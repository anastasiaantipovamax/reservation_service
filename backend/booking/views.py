from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Booking, MenuItem, Notification, RestaurantTable
from .permissions import IsAdminOrReadOnly, IsAdminUser
from .serializers import (
    BookingSerializer,
    BookingStatusSerializer,
    MenuItemSerializer,
    NotificationSerializer,
    RegisterSerializer,
    RestaurantTableSerializer,
    UserSerializer,
)
from .services import create_booking_notification, export_bookings_csv, export_bookings_pdf, is_table_available


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            return Response({'detail': 'Неверный логин или пароль.'}, status=status.HTTP_400_BAD_REQUEST)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class RestaurantTableViewSet(viewsets.ModelViewSet):
    queryset = RestaurantTable.objects.all()
    serializer_class = RestaurantTableSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        return queryset


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_available=True)
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__iexact=category)
        return queryset


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Booking.objects.select_related('user', 'table').prefetch_related('files')
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        booking = serializer.save(user=self.request.user)
        create_booking_notification(booking, action='created')

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def status(self, request, pk=None):
        booking = self.get_object()
        serializer = BookingStatusSerializer(booking, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        action = 'confirmed' if booking.status == Booking.STATUS_CONFIRMED else 'cancelled'
        create_booking_notification(booking, action=action)
        return Response(BookingSerializer(booking, context={'request': request}).data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def availability(self, request):
        table_id = request.query_params.get('table')
        date = request.query_params.get('date')
        time_start = request.query_params.get('time_start')
        time_end = request.query_params.get('time_end')
        if not all([table_id, date, time_start, time_end]):
            return Response({'detail': 'Нужно указать table, date, time_start, time_end.'}, status=400)
        try:
            table = RestaurantTable.objects.get(id=table_id)
        except RestaurantTable.DoesNotExist:
            return Response({'detail': 'Столик не найден.'}, status=404)
        available = is_table_available(table, date, time_start, time_end)
        return Response({'available': available})


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['patch'])
    def read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response(NotificationSerializer(notification).data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def export_csv(request):
    bookings = Booking.objects.select_related('user', 'table').all()
    content = export_bookings_csv(bookings)
    response = HttpResponse(content, content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="bookings_report.csv"'
    return response


@api_view(['GET'])
@permission_classes([IsAdminUser])
def export_pdf(request):
    bookings = Booking.objects.select_related('user', 'table').all()
    content = export_bookings_pdf(bookings)
    response = HttpResponse(content, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="bookings_report.pdf"'
    return response
