from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from booking.models import MenuItem, RestaurantTable


class Command(BaseCommand):
    help = 'Create demo users, tables and menu items.'

    def handle(self, *args, **options):
        admin, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True})
        admin.set_password('admin12345')
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()

        user, _ = User.objects.get_or_create(username='user', defaults={'email': 'user@example.com'})
        user.set_password('user12345')
        user.save()

        for number, capacity in [(1, 2), (2, 4), (3, 4), (4, 6), (5, 8)]:
            RestaurantTable.objects.get_or_create(number=number, defaults={'capacity': capacity, 'description': f'Столик на {capacity} гостей'})

        items = [
            ('Паста карбонара', 'Горячие блюда', 690),
            ('Цезарь с курицей', 'Салаты', 520),
            ('Тирамису', 'Десерты', 390),
            ('Лимонад', 'Напитки', 250),
        ]
        for name, category, price in items:
            MenuItem.objects.get_or_create(name=name, defaults={'category': category, 'price': price, 'description': 'Демонстрационная позиция меню'})

        self.stdout.write(self.style.SUCCESS('Demo data created. Admin: admin/admin12345, user: user/user12345'))
