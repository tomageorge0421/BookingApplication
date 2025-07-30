from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Avg
from ..models import Hotel, HotelReview
from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def hotels_view(request):
    hotels = Hotel.objects.annotate(avg_rating=Avg('reservation__hotelreview__rating'))
    
    location = request.GET.get('location')
    room_type = request.GET.get('room_type')
    max_price = request.GET.get('max_price')
    min_rating = request.GET.get('min_rating')

    if location:
        hotels = hotels.filter(location__icontains=location)
    if room_type:
        hotels = hotels.filter(available_types__icontains=room_type)
    if max_price:
        hotels = hotels.filter(price_per_night__lte=max_price)
    if min_rating:
        hotels = hotels.filter(avg_rating__gte=min_rating)

    return render(request, 'booking/hotels.html', {'hotels': hotels})


@login_required
def hotel_detail_view(request, hotel_id):
    hotel = Hotel.objects.get(id=hotel_id)
    reviews = HotelReview.objects.filter(reservation__hotel=hotel).select_related('reservation__user').order_by('-date_posted')
    avg_rating = reviews.aggregate(average=Avg('rating'))['average']


    return render(request, 'booking/hotel_detail.html', {
        'hotel': hotel,
        'reviews': reviews,
        'avg_rating': avg_rating,
    })

@staff_member_required
def update_hotel_view(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    error = None

    if request.method == 'POST':
        hotel.name = request.POST['name']
        hotel.location = request.POST['location']
        hotel.description = request.POST['description']
        hotel.available_types = request.POST['available_types']
        hotel.price_per_night = request.POST['price_per_night']
        hotel.save()
        return redirect('hotel_detail', hotel_id=hotel.id)

    return render(request, 'booking/update_hotel.html', {
        'hotel': hotel,
        'error': error
    })

@staff_member_required
def delete_hotel_view(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)

    has_active_reservations = hotel.reservation_set.filter(end_date__gte=date.today()).exists()

    if has_active_reservations:
        hotel.is_active = False  # Mark it as inactive
        hotel.save()
    else:
        hotel.delete()

    return redirect('hotels')

@staff_member_required
def create_hotel_view(request):
    error = None

    if request.method == 'POST':
        name = request.POST['name']
        location = request.POST['location']
        description = request.POST['description']
        available_types = request.POST['available_types']
        price_per_night = request.POST['price_per_night']

        if not all([name, location, description, available_types, price_per_night]):
            error = "Toate câmpurile sunt obligatorii."
        else:
            Hotel.objects.create(
                name=name,
                location=location,
                description=description,
                available_types=available_types,
                price_per_night=price_per_night
            )
            return redirect('hotels')

    return render(request, 'booking/create_hotel.html', {
        'error': error,
        'hotel':Hotel()
        })

@staff_member_required
def make_hotel_active_view(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)

    if hotel.is_active:
        messages.warning(request, "Hotelul este deja activ.")
    else:
        hotel.is_active = True
        hotel.save()
        messages.success(request, f"Hotelul {hotel.name} a fost activat cu succes.")

    return redirect('hotel_detail', hotel_id=hotel.id)
