import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import Booking, BookingFile, MenuItem, Notification, RestaurantTable
from .services import is_table_available


TEST_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT, EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ReservationServiceAPITests(APITestCase):
    """Automatic tests for the main reservation service scenarios."""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin12345',
        )
        self.user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='user12345',
        )
        self.admin_token = Token.objects.create(user=self.admin)
        self.user_token = Token.objects.create(user=self.user)
        self.table = RestaurantTable.objects.create(number=1, capacity=4, description='Table near the window')
        self.menu_item = MenuItem.objects.create(
            name='Pasta',
            description='Fresh pasta',
            price='590.00',
            category='Main course',
        )

    def auth_as_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')

    def auth_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')

    def test_user_can_register_and_login(self):
        register_response = self.client.post('/api/auth/register/', {
            'username': 'new_user',
            'email': 'new_user@example.com',
            'password': 'newpass123',
        }, format='json')
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', register_response.data)

        login_response = self.client.post('/api/auth/login/', {
            'username': 'new_user',
            'password': 'newpass123',
        }, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('token', login_response.data)

    def test_table_availability_is_detected(self):
        Booking.objects.create(
            user=self.user,
            table=self.table,
            date='2026-06-10',
            time_start='18:00',
            time_end='20:00',
            guests_count=2,
        )

        self.assertFalse(is_table_available(self.table, '2026-06-10', '19:00', '21:00'))
        self.assertTrue(is_table_available(self.table, '2026-06-10', '20:00', '21:00'))

    def test_user_can_create_booking_and_get_notification_and_pdf(self):
        self.auth_as_user()
        response = self.client.post('/api/bookings/', {
            'table': self.table.id,
            'date': '2026-06-11',
            'time_start': '17:00',
            'time_end': '19:00',
            'guests_count': 3,
            'comment': 'Window table, please',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        booking = Booking.objects.get(id=response.data['id'])
        self.assertEqual(booking.user, self.user)
        self.assertTrue(Notification.objects.filter(user=self.user, booking=booking).exists())
        self.assertTrue(BookingFile.objects.filter(booking=booking, file_type='pdf').exists())
        self.assertTrue(booking.pdf_path)

    def test_overlapping_booking_is_rejected(self):
        Booking.objects.create(
            user=self.user,
            table=self.table,
            date='2026-06-12',
            time_start='18:00',
            time_end='20:00',
            guests_count=2,
        )
        self.auth_as_user()
        response = self.client.post('/api/bookings/', {
            'table': self.table.id,
            'date': '2026-06-12',
            'time_start': '19:00',
            'time_end': '21:00',
            'guests_count': 2,
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Столик занят', str(response.data))

    def test_regular_user_cannot_create_table_but_admin_can_upload_table_image(self):
        self.auth_as_user()
        user_response = self.client.post('/api/tables/', {
            'number': 2,
            'capacity': 2,
            'description': 'Small table',
            'is_active': True,
        }, format='json')
        self.assertEqual(user_response.status_code, status.HTTP_403_FORBIDDEN)

        self.auth_as_admin()
        image = SimpleUploadedFile('table.png', (b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfeA\x0b\xbf\xb4\x00\x00\x00\x00IEND\xaeB`\x82'), content_type='image/png')
        admin_response = self.client.post('/api/tables/', {
            'number': 2,
            'capacity': 2,
            'description': 'Small table',
            'is_active': True,
            'image': image,
        }, format='multipart')
        self.assertEqual(admin_response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(RestaurantTable.objects.get(number=2).image)

    def test_admin_can_upload_menu_item_image(self):
        self.auth_as_admin()
        image = SimpleUploadedFile('dish.png', (b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfeA\x0b\xbf\xb4\x00\x00\x00\x00IEND\xaeB`\x82'), content_type='image/png')
        response = self.client.post('/api/menu/', {
            'name': 'Cheesecake',
            'description': 'Dessert',
            'price': '350.00',
            'category': 'Dessert',
            'is_available': True,
            'image': image,
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(MenuItem.objects.get(name='Cheesecake').image)

    def test_admin_can_export_reports(self):
        Booking.objects.create(
            user=self.user,
            table=self.table,
            date='2026-06-13',
            time_start='12:00',
            time_end='13:00',
            guests_count=2,
        )
        self.auth_as_admin()

        csv_response = self.client.get('/api/reports/export/csv/')
        self.assertEqual(csv_response.status_code, status.HTTP_200_OK)
        self.assertIn('text/csv', csv_response['Content-Type'])

        pdf_response = self.client.get('/api/reports/export/pdf/')
        self.assertEqual(pdf_response.status_code, status.HTTP_200_OK)
        self.assertEqual(pdf_response['Content-Type'], 'application/pdf')
