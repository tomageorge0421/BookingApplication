from django.shortcuts import render, redirect, get_object_or_404
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from ..models import Reservation, Hotel
from django.contrib.auth import get_user_model
from datetime import date
from django.http import HttpResponseForbidden

User = get_user_model()


@login_required
def reserve_view(request, hotel_id):
    hotel = Hotel.objects.get(id=hotel_id)
    error = None
    success = None

    if request.method == 'POST':
        start_date = parse_date(request.POST['start_date'])
        end_date = parse_date(request.POST['end_date'])

        if not start_date or not end_date:
            error = "Ambele date sunt necesare."
        elif end_date <= start_date:
            error = "Data de final trebuie să fie după data de început."
        else:
            try:
                reservation = Reservation.objects.create(
                    user=request.user,
                    hotel=hotel,
                    start_date=start_date,
                    end_date=end_date
                )
                success = "Rezervarea a fost realizată cu succes!"
            except ValidationError as e:
                error = str(e)

    return render(request, 'booking/reserve.html', {
        'hotel': hotel,
        'error': error,
        'success': success
    })    

@login_required
def my_reservations_view(request):
    reservations = Reservation.objects.filter(user=request.user).select_related('hotel')
    return render(request, 'booking/my_reservations.html', {
        'reservations': reservations,
        'today': date.today(),
    })

@staff_member_required
def all_reservations_view(request):
    reservations = Reservation.objects.select_related('user', 'hotel').all().order_by('-start_date')
    return render(request, 'booking/list.html', {
        'reservations': reservations
    })

@staff_member_required
def create_reservation_admin(request):
    if request.method == 'POST':
        user_id = request.POST.get('user')
        hotel_id = request.POST.get('hotel')
        start_date = parse_date(request.POST.get('start_date'))
        end_date = parse_date(request.POST.get('end_date'))

        user = User.objects.get(id=user_id)
        hotel = Hotel.objects.get(id=hotel_id)

        nights = (end_date - start_date).days
        room_type = hotel.available_types  # presupunem că e un string (ex: "1P")
        total_price = nights * hotel.price_per_night

        Reservation.objects.create(
            user=user,
            hotel=hotel,
            start_date=start_date,
            end_date=end_date,
            room_type=room_type,
            total_price=total_price
        )
        return redirect('admin_reservations')

    users = User.objects.all()
    hotels = Hotel.objects.all()
    return render(request, 'booking/create_reservation.html', {
        'users': users,
        'hotels': hotels
    })

@staff_member_required
def delete_reservation_admin(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    if request.method == 'POST':
        reservation.delete()
        return redirect('admin_reservations')
    return render(request, 'booking/delete_reservation_confirm.html', {
        'reservation': reservation
    })

@staff_member_required
def update_reservation_admin(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)

    if request.method == 'POST':
        user_id = request.POST.get('user')
        hotel_id = request.POST.get('hotel')
        start_date = parse_date(request.POST.get('start_date'))
        end_date = parse_date(request.POST.get('end_date'))

        if start_date > end_date:
            users = User.objects.all()
            hotels = Hotel.objects.all()
            return render(request, 'booking/update_reservation.html', {
                'reservation': reservation,
                'users': users,
                'hotels': hotels,
                'error': 'Data de început nu poate fi după data de sfârșit.'
            })

        user = User.objects.get(id=user_id)
        hotel = Hotel.objects.get(id=hotel_id)

        nights = (end_date - start_date).days
        room_type = hotel.available_types
        total_price = nights * hotel.price_per_night

        reservation.user = user
        reservation.hotel = hotel
        reservation.start_date = start_date
        reservation.end_date = end_date
        reservation.room_type = room_type
        reservation.total_price = total_price
        reservation.save()

        return redirect('admin_reservations')

    users = User.objects.all()
    hotels = Hotel.objects.all()
    return render(request, 'booking/update_reservation.html', {
        'reservation': reservation,
        'users': users,
        'hotels': hotels
    })

@login_required
def cancel_reservation_view(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    days_before_checkin = (reservation.start_date - date.today()).days

    if days_before_checkin < 2:
        return HttpResponseForbidden("Rezervarea nu mai poate fi anulată cu mai puțin de 2 zile înainte.")

    if request.method == 'POST':
        reservation.delete()
        return redirect('my_reservations')

    return render(request, 'booking/cancel_reservation_confirm.html', {
        'reservation': reservation
    })