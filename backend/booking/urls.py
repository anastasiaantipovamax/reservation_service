from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BookingViewSet,
    LoginView,
    MeView,
    MenuItemViewSet,
    NotificationViewSet,
    RegisterView,
    RestaurantTableViewSet,
    export_csv,
    export_pdf,
)

router = DefaultRouter()
router.register('tables', RestaurantTableViewSet, basename='tables')
router.register('menu', MenuItemViewSet, basename='menu')
router.register('bookings', BookingViewSet, basename='bookings')
router.register('notifications', NotificationViewSet, basename='notifications')

urlpatterns = [
    path('auth/register/', RegisterView.as_view()),
    path('auth/login/', LoginView.as_view()),
    path('auth/me/', MeView.as_view()),
    path('reports/export/csv/', export_csv),
    path('reports/export/pdf/', export_pdf),
    path('', include(router.urls)),
]
