from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from ..models import HotelReview, Reservation

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
def update_review_view(request, review_id):
    review = get_object_or_404(HotelReview, pk=review_id)
    
    if request.method == 'POST':
        review.text = request.POST['text']
        review.rating = request.POST['rating']
        review.save()
        return redirect('hotel_detail', hotel_id=review.reservation.hotel.id)
    
    return render(request, 'booking/update_review.html', {'review': review})


@staff_member_required
def delete_review_view(request, review_id):
    review = get_object_or_404(HotelReview, pk=review_id)
    hotel_id = review.reservation.hotel.id
    review.delete()
    return redirect('hotel_detail', hotel_id=hotel_id)

@staff_member_required
def create_review_view(request):
    error = None
    success = None

    if request.method == 'POST':
        reservation_id = request.POST.get('reservation_id')
        rating = request.POST.get('rating')
        text = request.POST.get('text')

        try:
            reservation = Reservation.objects.get(id=reservation_id)

            if hasattr(reservation, 'hotelreview'):
                error = "Această rezervare are deja o recenzie."
            else:
                HotelReview.objects.create(
                    reservation=reservation,
                    rating=rating,
                    text=text
                )
                success = "Recenzia a fost adăugată cu succes."

        except Reservation.DoesNotExist:
            error = "Rezervarea nu a fost găsită."

    eligible_reservations = Reservation.objects.filter(
        hotelreview__isnull=True
    ).select_related('user', 'hotel')

    return render(request, 'booking/create_review.html', {
        'reservations': eligible_reservations,
        'error': error,
        'success': success
    })

@login_required
def update_own_review(request, review_id):
    review = get_object_or_404(HotelReview, id=review_id)

    if review.user != request.user:
        return HttpResponseForbidden("Nu ai permisiunea să editezi această recenzie.")

    if request.method == 'POST':
        review.rating = request.POST['rating']
        review.text = request.POST['text']
        review.save()
        return redirect('hotel_detail', review.hotel.id)

    return render(request, 'booking/update_review.html', {'review': review})


@login_required
def delete_own_review(request, review_id):
    review = get_object_or_404(HotelReview, id=review_id)

    if review.user != request.user:
        return HttpResponseForbidden("Nu ai permisiunea să ștergi această recenzie.")

    if request.method == 'POST':
        hotel_id = review.hotel.id
        review.delete()
        return redirect('hotel_detail', hotel_id)

    return render(request, 'booking/confirm_delete_review.html', {'review': review})