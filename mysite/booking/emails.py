from django.core.mail import send_mail
from django.conf import settings

def send_reservation_reminder(reservation):
    subject = f"Reamintire rezervare hotel {reservation.hotel.name}"
    message = (
        f"Salut {reservation.user.first_name},\n\n"
        f"Te informăm că sejurul tău la hotelul {reservation.hotel.name} începe peste 3 zile!\n"
        f"Detalii rezervare:\n"
        f"- Check-in: {reservation.start_date}\n"
        f"- Check-out: {reservation.end_date}\n"
        f"- Tip cameră: {reservation.room_type}\n"
        f"- Preț total: {reservation.total_price} RON\n\n"
        f"Te așteptăm cu drag!\n"
    )
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [reservation.user.email]

    send_mail(subject, message, from_email, recipient_list)
