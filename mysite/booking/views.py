from django.shortcuts import render

from django.http import HttpResponse

from django.contrib.auth import authenticate, login as auth_login
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

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






