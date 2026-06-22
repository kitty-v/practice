from django.shortcuts import render
from django.contrib.auth.models import User
from items.models import Item, Category

def home(request):
    categories = Category.objects.all()
    recent_items = Item.objects.filter(status='active').select_related('seller', 'category').order_by('-created_at')[:12]
    return render(request, 'core/home.html', {
        'categories': categories,
        'recent_items': recent_items,
        'total_items': Item.objects.filter(status='active').count(),
        'total_users': User.objects.count(),
        'category_count': categories.count(),
    })
