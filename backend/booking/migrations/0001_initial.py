# Generated for course project
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, verbose_name='Название')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('price', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Цена')),
                ('category', models.CharField(blank=True, max_length=80, verbose_name='Категория')),
                ('image', models.ImageField(blank=True, null=True, upload_to='uploads/menu/', verbose_name='Изображение')),
                ('is_available', models.BooleanField(default=True, verbose_name='Доступно')),
            ],
            options={'verbose_name': 'Блюдо меню', 'verbose_name_plural': 'Блюда меню', 'ordering': ['category', 'name']},
        ),
        migrations.CreateModel(
            name='RestaurantTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveIntegerField(unique=True, verbose_name='Номер столика')),
                ('capacity', models.PositiveIntegerField(verbose_name='Количество мест')),
                ('description', models.CharField(blank=True, max_length=255, verbose_name='Описание')),
                ('image', models.ImageField(blank=True, null=True, upload_to='uploads/tables/', verbose_name='Изображение')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
            ],
            options={'verbose_name': 'Столик', 'verbose_name_plural': 'Столики', 'ordering': ['number']},
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Дата')),
                ('time_start', models.TimeField(verbose_name='Время начала')),
                ('time_end', models.TimeField(verbose_name='Время окончания')),
                ('guests_count', models.PositiveIntegerField(default=1, verbose_name='Количество гостей')),
                ('status', models.CharField(choices=[('pending', 'Ожидает подтверждения'), ('confirmed', 'Подтверждено'), ('cancelled', 'Отменено'), ('completed', 'Завершено')], default='pending', max_length=20)),
                ('comment', models.TextField(blank=True, verbose_name='Комментарий')),
                ('pdf_path', models.CharField(blank=True, max_length=255, verbose_name='PDF-подтверждение')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('table', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bookings', to='booking.restauranttable')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Бронирование', 'verbose_name_plural': 'Бронирования', 'ordering': ['-date', '-time_start']},
        ),
        migrations.CreateModel(
            name='BookingFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='confirmations/')),
                ('file_type', models.CharField(default='pdf', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='booking.booking')),
            ],
            options={'verbose_name': 'Файл бронирования', 'verbose_name_plural': 'Файлы бронирования', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=160)),
                ('message', models.TextField()),
                ('delivery_channel', models.CharField(choices=[('site', 'Внутри сайта'), ('email', 'Email'), ('site_email', 'Сайт и email')], default='site_email', max_length=20)),
                ('email_status', models.CharField(choices=[('not_sent', 'Не отправлено'), ('sent', 'Отправлено'), ('error', 'Ошибка отправки')], default='not_sent', max_length=20)),
                ('is_read', models.BooleanField(default=False)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('booking', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='booking.booking')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Уведомление', 'verbose_name_plural': 'Уведомления', 'ordering': ['-created_at']},
        ),
    ]
