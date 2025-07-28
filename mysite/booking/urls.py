from django.urls import path
from .views import create_review_view


from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("register/details/", views.register_details_view, name="register_details"),
    path("hotels/", views.hotels_view, name="hotels"),
    path("hotels/<int:hotel_id>/", views.hotel_detail_view, name="hotel_detail"),
    path("hotels/<int:hotel_id>/reserve/", views.reserve_view, name="reserve_hotel"),
    path("my-reservations/", views.my_reservations_view, name="my_reservations"),
    path("review/<int:reservation_id>/", views.leave_review_view, name="leave_review"),
    path("hotels/<int:hotel_id>/update/", views.update_hotel_view, name="update_hotel"),
    path("hotels/<int:hotel_id>/delete/", views.delete_hotel_view, name="delete_hotel"),
    path("hotels/create/", views.create_hotel_view, name="create_hotel"),
    path("reviews/<int:review_id>/update/", views.update_review_view, name="update_review"),
    path("reviews/<int:review_id>/delete/", views.delete_review_view, name="delete_review"),
    path('admin/create_review/', create_review_view, name='create_review'),


]