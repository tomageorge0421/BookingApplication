from django.urls import path


from . import views

from .views import create_reservation_admin, all_reservations_view

from django.contrib.auth.views import LogoutView




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
    path('admin/create_review/', views.create_review_view, name='create_review'),
    path('admin/reservations/', all_reservations_view, name='admin_reservations'),
    path('admin/reservations/create/', create_reservation_admin, name='create_reservation_admin'),
    path('admin/reservations/<int:reservation_id>/delete/', views.delete_reservation_admin, name='delete_reservation_admin'),
    path('admin/reservations/<int:reservation_id>/update/', views.update_reservation_admin, name='update_reservation_admin'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
]