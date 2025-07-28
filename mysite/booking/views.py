from django.shortcuts import render

from django.http import HttpResponse

from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.shortcuts import redirect
from .models import CustomUser, Reservation
from django.contrib.auth.decorators import login_required

from django.db.models import Avg, Q
from .models import Hotel, HotelReview

from django.utils.dateparse import parse_date
from django.core.exceptions import ValidationError

from datetime import date

from django.shortcuts import get_object_or_404

from django.contrib.admin.views.decorators import staff_member_required

# Create your views here.

def index(request):
    return render(request, 'booking/index.html')

def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            return redirect('hotels')  # sau către pagina principală reală
        else:
            error = "Username sau parolă incorectă."
    return render(request, 'booking/login.html', {'error': error})

def register_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        age = request.POST['age']
        profession = request.POST['profession']
        if CustomUser.objects.filter(username=username).exists():
            error = "Username-ul este deja folosit."
        else:
            user = CustomUser.objects.create_user(username=username, password=password, age=age, profession=profession)
            auth_login(request, user)#asta cred ca se poate comenta/sterge
            return redirect('register_details')
    return render(request, 'booking/register.html', {'error': error})

@login_required
def register_details_view(request):
    error = None
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']

        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        return redirect('index')  # sau redirect unde vrei
    return render(request, 'booking/register_details.html', {'error': error})

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


@login_required
def leave_review_view(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    if request.method == 'POST':
        rating = int(request.POST['rating'])
        text = request.POST['text']

        # Verificăm dacă rezervarea are deja review (OneToOneField garantează unicitate)
        if hasattr(reservation, 'hotelreview'):
            # Dacă există deja review, redirecționăm spre rezervări
            return redirect('my_reservations')

        HotelReview.objects.create(
            reservation=reservation,
            rating=rating,
            text=text
        )
        return redirect('my_reservations')

    return render(request, 'booking/leave_review.html', {
        'reservation': reservation
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