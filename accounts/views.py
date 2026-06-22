from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Avg, Count
from .forms import RegisterForm, ProfileForm
from items.models import Item, Favorite, Message, Review, Order, RevenueRecord

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
    received_reviews = Review.objects.filter(reviewee=user).select_related('reviewer', 'item').order_by('-created_at')
    rating_stats = received_reviews.aggregate(avg=Avg('rating'), count=Count('id'))
    return render(request, 'accounts/profile.html', {
        'profile_user': user,
        'items': items,
        'received_reviews': received_reviews,
        'avg_rating': rating_stats['avg'],
        'review_count': rating_stats['count'],
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
    my_orders = Order.objects.filter(buyer=request.user).select_related('seller', 'item', 'item__category').order_by('-created_at')
    my_sold_orders = Order.objects.filter(seller=request.user).select_related('buyer', 'item', 'item__category').order_by('-created_at')
    recent_messages = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).select_related('sender', 'receiver').order_by('-created_at')[:10]
    return render(request, 'accounts/dashboard.html', {
        'my_items': my_items,
        'my_orders': my_orders,
        'my_sold_orders': my_sold_orders,
        'my_favorites': my_favorites,
        'unread_count': unread_count,
        'recent_messages': recent_messages,
    })

@login_required
def balance(request):
    from django.db.models import Sum
    from datetime import timedelta
    from django.utils import timezone

    profile = request.user.profile
    # Revenue history for last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    revenues = RevenueRecord.objects.filter(
        seller=request.user, created_at__gte=thirty_days_ago
    ).order_by('created_at')
    total_revenue = revenues.aggregate(total=Sum('amount'))['total'] or 0

    # Calculate percentages for chart bars
    max_amount = max([r.amount for r in revenues], default=0)
    revenue_history = []
    for r in revenues:
        pct = (r.amount / max_amount * 100) if max_amount > 0 else 0
        revenue_history.append({'amount': r.amount, 'pct': float(pct)})

    return render(request, 'accounts/balance.html', {
        'balance': profile.balance,
        'total_revenue': total_revenue,
        'revenue_history': revenue_history,
    })

@login_required
def recharge(request):
    """充值接口 — MOCK 实现，预留真实支付接入"""
    if request.method == 'POST':
        amount = request.POST.get('amount', '0')
        try:
            amount = Decimal(str(amount))
            if amount <= 0:
                messages.error(request, '充值金额必须大于零')
                return redirect('accounts:balance')
            if amount > Decimal('100000'):
                messages.error(request, '单次充值金额不能超过 100,000 元')
                return redirect('accounts:balance')
        except ValueError:
            messages.error(request, '请输入有效金额')
            return redirect('accounts:balance')

        # TODO: 接入真实支付网关
        # 模拟支付成功
        profile = request.user.profile
        profile.balance += amount
        profile.save(update_fields=['balance'])

        messages.success(request, f'充值成功！已到账 ¥{amount:.2f}')
        return redirect('accounts:balance')

    return redirect('accounts:balance')
