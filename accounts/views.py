from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegisterForm, ProfileForm
from items.models import Item, Favorite, Message

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '注册成功！欢迎来到闲鱼集市。')
            return redirect('core:home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    items = Item.objects.filter(seller=user).order_by('-created_at')
    return render(request, 'accounts/profile.html', {
        'profile_user': user,
        'items': items,
    })

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, '资料已更新。')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user.profile)
    return render(request, 'accounts/edit_profile.html', {'form': form})

@login_required
def dashboard(request):
    my_items = Item.objects.filter(seller=request.user).order_by('-created_at')
    my_favorites = Favorite.objects.filter(user=request.user).select_related('item__seller').order_by('-created_at')
    unread_count = Message.objects.filter(receiver=request.user, is_read=False).count()
    return render(request, 'accounts/dashboard.html', {
        'my_items': my_items,
        'my_favorites': my_favorites,
        'unread_count': unread_count,
    })
