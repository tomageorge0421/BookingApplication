from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from ..models.review import HotelReview
from ..models.review_vote import ReviewVote

@login_required
def vote_review(request, review_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    review = get_object_or_404(HotelReview, id=review_id)
    user = request.user

    if review.user == user:
        return HttpResponseForbidden("Nu poți vota propriul review.")

    vote_type = request.POST.get('vote')  # expected 'up' or 'down'
    if vote_type not in ['up', 'down']:
        return JsonResponse({'error': 'Vote invalid'}, status=400)

    value = ReviewVote.UPVOTE if vote_type == 'up' else ReviewVote.DOWNVOTE

    vote_obj, created = ReviewVote.objects.get_or_create(user=user, review=review, defaults={'value': value})
    if not created:
        if vote_obj.value == value:
            # dacă dă din nou același vot, îl putem elimina (toggle) sau ignora; alegem toggle: ștergem
            vote_obj.delete()
        else:
            # schimbă votul (up -> down sau invers)
            vote_obj.value = value
            vote_obj.save()

    # răspuns poate fi redirecționat sau JSON pentru AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'score': review.score,
            'upvotes': review.upvotes,
            'downvotes': review.downvotes,
        })
    return redirect('hotel_detail', hotel_id=review.hotel.id)
