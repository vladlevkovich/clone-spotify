from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.db import transaction
from .models import *
from ..core.models import Profile
from .forms import *
from config import settings


def user_register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    context = {
        'form': form
    }
    return render(request, 'users/register.html', context)


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = UserLoginForm()
    context = {
        'form': form
    }
    return render(request, 'users/login.html', context)


def user_logout(request):
    logout(request)
    return redirect('home')


# @login_required()
# def follow(request, user_pk):
#     user = request.user
#     following = get_object_or_404(Profile, pk=user_pk)
#     f, create = Follow.objects.get_or_create(follower=user, following=following)
