from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum, Count, Q

class HotelReview(models.Model):
    reservation = models.OneToOneField('booking.Reservation', on_delete=models.CASCADE, null=True, blank=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField(blank=True)
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user = self.user.username if self.user else "Utilizator necunoscut"
        hotel = self.hotel.name if self.hotel else "Hotel necunoscut"
        return f"Review de la {user} pentru {hotel} - {self.rating}★"

    @property
    def user(self):
        if self.reservation:
            return self.reservation.user
        return None  # sau poți returna un string, ex: "Utilizator necunoscut"

    @property
    def hotel(self):
        if self.reservation:
            return self.reservation.hotel
        return None
    
    @property
    def score(self):
        agg = self.votes.aggregate(total=Sum('value'))
        return agg['total'] or 0  # upvotes minus downvotes

    @property
    def upvotes(self):
        from booking.models.review_vote import ReviewVote
        return self.votes.filter(value=ReviewVote.UPVOTE).count()

    @property
    def downvotes(self):
        from booking.models.review_vote import ReviewVote
        return self.votes.filter(value=ReviewVote.DOWNVOTE).count()


