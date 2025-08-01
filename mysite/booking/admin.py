from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Hotel, HotelReview, Reservation, ReviewVote

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ("Informații suplimentare", {'fields': ('age', 'profession')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Informații suplimentare", {'fields': ('age', 'profession')}),
    )

class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'average_rating_display')

    def average_rating_display(self, obj):
        avg = obj.average_rating()
        return avg if avg is not None else '-'
    average_rating_display.short_description = 'Average Rating'    

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'hotel', 'room_type', 'start_date', 'end_date', 'total_price')
    readonly_fields = ('room_type', 'total_price')  # doar ca să le vezi

class ReviewVoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'review', 'value')
    list_filter = ('value',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Hotel, HotelAdmin)
admin.site.register(HotelReview)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(ReviewVote, ReviewVoteAdmin)
