import csv
import os
from datetime import datetime
from io import BytesIO, StringIO

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.db.models import Q
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .models import Booking, BookingFile, Notification


def is_table_available(table, date, time_start, time_end, exclude_booking_id=None):
    query = Booking.objects.filter(
        table=table,
        date=date,
        status__in=[Booking.STATUS_PENDING, Booking.STATUS_CONFIRMED],
    ).filter(time_start__lt=time_end, time_end__gt=time_start)
    if exclude_booking_id:
        query = query.exclude(id=exclude_booking_id)
    return not query.exists()


def make_confirmation_pdf(booking):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    pdf.setTitle(f'booking-{booking.id}')
    pdf.setFont('Helvetica-Bold', 16)
    pdf.drawString(70, height - 70, 'RestaurantBook - booking confirmation')
    pdf.setFont('Helvetica', 11)
    rows = [
        ('Booking ID', str(booking.id)),
        ('User', booking.user.username),
        ('Email', booking.user.email or '-'),
        ('Table', str(booking.table.number)),
        ('Guests', str(booking.guests_count)),
        ('Date', booking.date.strftime('%d.%m.%Y')),
        ('Time', f'{booking.time_start.strftime("%H:%M")} - {booking.time_end.strftime("%H:%M")}'),
        ('Status', booking.get_status_display()),
    ]
    y = height - 120
    for name, value in rows:
        pdf.setFont('Helvetica-Bold', 11)
        pdf.drawString(70, y, f'{name}:')
        pdf.setFont('Helvetica', 11)
        pdf.drawString(180, y, value)
        y -= 24
    pdf.setFont('Helvetica', 9)
    pdf.drawString(70, 70, 'Generated automatically by reservation service.')
    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


def attach_confirmation_pdf(booking):
    pdf_bytes = make_confirmation_pdf(booking)
    filename = f'booking_{booking.id}_confirmation.pdf'
    booking_file = BookingFile.objects.create(booking=booking)
    booking_file.file.save(filename, ContentFile(pdf_bytes), save=True)
    booking.pdf_path = booking_file.file.name
    booking.save(update_fields=['pdf_path'])
    return booking_file


def send_booking_email(notification, booking_file=None):
    user = notification.user
    if not user.email:
        notification.email_status = Notification.EMAIL_ERROR
        notification.save(update_fields=['email_status'])
        return False

    email = EmailMessage(
        subject=notification.title,
        body=notification.message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    if booking_file and booking_file.file:
        email.attach_file(booking_file.file.path)
    try:
        email.send(fail_silently=False)
        notification.email_status = Notification.EMAIL_SENT
        notification.sent_at = timezone.now()
        notification.save(update_fields=['email_status', 'sent_at'])
        return True
    except Exception:
        notification.email_status = Notification.EMAIL_ERROR
        notification.save(update_fields=['email_status'])
        return False


def create_booking_notification(booking, action='created'):
    titles = {
        'created': 'Бронирование создано',
        'confirmed': 'Бронирование подтверждено',
        'cancelled': 'Бронирование отменено',
    }
    title = titles.get(action, 'Уведомление о бронировании')
    message = (
        f'Ваше бронирование столика {booking.table.number} на {booking.date.strftime("%d.%m.%Y")} '
        f'с {booking.time_start.strftime("%H:%M")} до {booking.time_end.strftime("%H:%M")} обработано системой. '
        f'Количество гостей: {booking.guests_count}. Статус: {booking.get_status_display()}.'
    )
    notification = Notification.objects.create(
        user=booking.user,
        booking=booking,
        title=title,
        message=message,
        delivery_channel=Notification.CHANNEL_BOTH,
    )
    booking_file = attach_confirmation_pdf(booking)
    send_booking_email(notification, booking_file)
    return notification


def export_bookings_csv(bookings):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['id', 'user', 'email', 'table', 'date', 'time_start', 'time_end', 'guests', 'status'])
    for booking in bookings:
        writer.writerow([
            booking.id,
            booking.user.username,
            booking.user.email,
            booking.table.number,
            booking.date,
            booking.time_start,
            booking.time_end,
            booking.guests_count,
            booking.status,
        ])
    return output.getvalue()


def export_bookings_pdf(bookings):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    pdf.setTitle('booking-report')
    pdf.setFont('Helvetica-Bold', 16)
    pdf.drawString(60, height - 60, 'RestaurantBook - bookings report')
    pdf.setFont('Helvetica', 10)
    y = height - 100
    for booking in bookings[:40]:
        row = (
            f'#{booking.id} | table {booking.table.number} | {booking.date} | '
            f'{booking.time_start}-{booking.time_end} | {booking.user.username} | {booking.status}'
        )
        pdf.drawString(60, y, row)
        y -= 18
        if y < 70:
            pdf.showPage()
            pdf.setFont('Helvetica', 10)
            y = height - 60
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()
