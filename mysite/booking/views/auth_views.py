from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import get_user_model
from ..models import CustomUser
from django.contrib.auth.decorators import login_required
from booking.models import Reservation, HotelReview, Hotel
from django.db.models import Avg, Count, Sum
from django.utils.timezone import now
from datetime import timedelta
from django.contrib import messages


User = get_user_model()

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
            if user.reservation_deleted_notification:
                messages.warning(request, "O rezervare ți-a fost ștearsă de către un administrator.")
                user.reservation_deleted_notification = False  # Resetăm flagul
                user.save()
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
            CustomUser.objects.create_user(username=username, password=password, age=age, profession=profession)
            # îl autentifici (asta returnează un user cu backend setat)
            user = authenticate(request, username=username, password=password)
            if user:
                auth_login(request, user)
                return redirect('register_details')
            else:
                error = "Ceva nu a mers la autentificare după înregistrare."
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
        user.profile_picture_url = request.POST.get('profile_picture_url')
        user.save()

        return redirect('index')  # sau redirect unde vrei
    return render(request, 'booking/register_details.html', {'error': error})

@login_required
def my_profile_view(request):
    user = request.user
    context = {'user': user}

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update':
            user.username = request.POST.get('username')
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.age = request.POST.get('age')
            user.profession = request.POST.get('profession')
            user.profile_picture_url = request.POST.get('profile_picture_url')
            user.save()
            return redirect('my_profile')

        elif action == 'delete':
            Reservation.objects.filter(user=user).delete()
            HotelReview.objects.filter(reservation__user=user).delete()
            user.delete()
            return redirect('index')

    if user.is_staff:
        # Admin dashboard
        today = now().date()
        seven_days_ago = today - timedelta(days=6)

        bookings_per_day = (
            Reservation.objects
            .filter(start_date__range=(seven_days_ago, today))
            .extra({'day': "date(start_date)"})
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )

        top_hotels = (
            Hotel.objects.annotate(avg_rating=Avg('reservation__hotelreview__rating'))
            .order_by('-avg_rating')[:5]
        )

        reviews_per_day = (
            HotelReview.objects
            .filter(date_posted__date__range=(seven_days_ago, today))
            .extra({'day': "date(date_posted)"})
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )

        context.update({
            'bookings_per_day': bookings_per_day,
            'top_hotels': top_hotels,
            'reviews_per_day': reviews_per_day,
            'is_admin': True,
        })
    else:
        # User dashboard
        reservations = Reservation.objects.filter(user=user)
        total_spent = reservations.aggregate(total=Sum('total_price'))['total'] or 0
        review_avg = HotelReview.objects.filter(reservation__user=user).aggregate(avg=Avg('rating'))['avg']

        context.update({
            'total_spent': total_spent,
            'num_reservations': reservations.count(),
            'average_rating': round(review_avg, 2) if review_avg else None,
            'is_admin': False,
        })

    return render(request, 'booking/my_profile.html', context)