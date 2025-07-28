from django.db import models
from django.conf import settings
from .hotel import Hotel

class Reservation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    room_type = models.CharField(max_length=3, choices=Hotel.HOTEL_TYPES, editable=False)
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.hotel.name} ({self.room_type})"

    def clean(self):
        if self.end_date <= self.start_date:
            from django.core.exceptions import ValidationError
            raise ValidationError("Data de final trebuie să fie după data de început.")

    def save(self, *args, **kwargs):
        self.room_type = self.hotel.available_types
        num_nights = (self.end_date - self.start_date).days
        self.total_price = self.hotel.price_per_night * num_nights
        super().save(*args, **kwargs)
