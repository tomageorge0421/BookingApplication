from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import get_user_model
from ..models import CustomUser
from django.contrib.auth.decorators import login_required

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
            user = CustomUser.objects.create_user(username=username, password=password, age=age, profession=profession)
            auth_login(request, user)#asta cred ca se poate comenta/sterge
            return redirect('register_details')
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
        user.save()

        return redirect('index')  # sau redirect unde vrei
    return render(request, 'booking/register_details.html', {'error': error})