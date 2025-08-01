from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Avg
from ..models import Hotel, HotelReview, ReviewVote
from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.db.models import Value, Sum, Avg
from django.db.models.functions import Coalesce, TruncDate

from django.shortcuts import render, get_object_or_404
from django.db.models import Avg, Value, Sum, IntegerField, FloatField
from django.db.models.functions import Coalesce
from ..models import Hotel, HotelReview
from ..models.review_vote import ReviewVote


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
    hotel = get_object_or_404(Hotel, id=hotel_id)

    # Filtrare opțională: ?min_score=2
    min_score = request.GET.get('min_score')
    
    reviews_qs = (
        HotelReview.objects
        .filter(reservation__hotel=hotel)
        .select_related('reservation__user')
        .annotate(annotated_score=Coalesce(Sum('votes__value'), Value(0), output_field=IntegerField()))
    )

    if min_score is not None:
        try:
            min_score_int = int(min_score)
            reviews_qs = reviews_qs.filter(score__gte=min_score_int)
        except ValueError:
            pass

    avg_rating = reviews_qs.aggregate(
        average=Coalesce(Avg('rating'), Value(0), output_field=FloatField())
    )['average']

    reviews_qs = reviews_qs.order_by('-annotated_score', '-date_posted')

    # Ce review-uri a votat userul curent pentru a ascunde butoanele
    voted_review_ids = []
    if request.user.is_authenticated:
        voted_review_ids = list(
            ReviewVote.objects.filter(
                user=request.user,
                review__reservation__hotel=hotel
            ).values_list('review_id', flat=True)
        )

    return render(request, 'booking/hotel_detail.html', {
        'hotel': hotel,
        'reviews': reviews_qs,
        'avg_rating': avg_rating,
        'voted_review_ids': voted_review_ids,
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
        photo_url = request.POST['photo_url']

        if not all([name, location, description, available_types, price_per_night]):
            error = "Toate câmpurile sunt obligatorii."
        else:
            Hotel.objects.create(
                name=name,
                location=location,
                description=description,
                available_types=available_types,
                price_per_night=price_per_night,
                photo_url=photo_url
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
