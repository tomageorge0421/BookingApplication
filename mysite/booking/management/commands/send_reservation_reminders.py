from django.core.management.base import BaseCommand
from django.utils.timezone import now
from datetime import timedelta
from booking.models import Reservation
from booking.emails import send_reservation_reminder

class Command(BaseCommand):
    help = 'Trimite notificări prin email cu 3 zile înainte de începutul rezervării'

    def handle(self, *args, **kwargs):
        print("Start trimitere remindere rezervari...")
        today = now().date()
        target_date = today + timedelta(days=4)
        reservations = Reservation.objects.filter(start_date=target_date)
        print(f"Rezervari gasite: {reservations.count()}")
        for reservation in reservations:
            print(f"Trimitem mail pentru rezervarea id={reservation.id} user={reservation.user.email}")
            send_reservation_reminder(reservation)
        print("Proces finalizat.")