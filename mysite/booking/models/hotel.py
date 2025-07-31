from django.db import models
from django.db.models import Avg
from booking.models.review import HotelReview

class Hotel(models.Model):
    HOTEL_TYPES = [
        ('1P', 'Cameră pentru 1 persoană'),
        ('2P', 'Cameră pentru 2 persoane'),
        ('3P', 'Cameră pentru 3 persoane'),
        ('APT', 'Apartament'),
    ]

    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField()
    available_types = models.CharField(max_length=3, choices=HOTEL_TYPES)
    price_per_night = models.DecimalField(max_digits=7, decimal_places=2)
    is_active = models.BooleanField(default=True)
    photo_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.location}"

    def average_rating(self):
        avg = HotelReview.objects.filter(reservation__hotel=self).aggregate(avg_rating=Avg('rating'))['avg_rating']
        if avg:
            return round(avg, 2)
        return None
