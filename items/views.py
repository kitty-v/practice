from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Item, Category, Favorite, Message
from .forms import ItemForm, MessageForm

def item_list(request):
    items = Item.objects.filter(status='active').select_related('seller', 'category').order_by('-created_at')
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')
    condition = request.GET.get('condition', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    if query:
        items = items.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    if category_slug:
        items = items.filter(category__slug=category_slug)
    if condition:
        items = items.filter(condition=condition)
    if min_price:
        items = items.filter(price__gte=min_price)
    if max_price:
        items = items.filter(price__lte=max_price)

    categories = Category.objects.all()
    return render(request, 'items/item_list.html', {
        'items': items,
        'categories': categories,
        'query': query,
        'current_category': category_slug,
        'current_condition': condition,
        'min_price': min_price,
        'max_price': max_price,
    })

def item_detail(request, pk):
    item = get_object_or_404(Item.objects.select_related('seller', 'category'), pk=pk)
    images = item.images.all()
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, item=item).exists()

    related_items = Item.objects.filter(
        category=item.category, status='active'
    ).exclude(pk=item.pk)[:4]

    form = MessageForm()
    if request.method == 'POST' and request.user.is_authenticated:
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.receiver = item.seller
            msg.item = item
            msg.save()
            messages.success(request, '消息已发送！')
            return redirect('items:item_detail', pk=item.pk)

    return render(request, 'items/item_detail.html', {
        'item': item,
        'images': images,
        'is_favorited': is_favorited,
        'related_items': related_items,
        'form': form,
    })

@login_required
def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.seller = request.user
            item.save()
            # Handle image uploads
            images = request.FILES.getlist('images')
            for i, img in enumerate(images):
                item.images.create(image=img, is_primary=(i == 0))
            messages.success(request, '商品发布成功！')
            return redirect('items:item_detail', pk=item.pk)
    else:
        form = ItemForm()
    return render(request, 'items/item_form.html', {'form': form, 'action': '发布'})

@login_required
def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if item.seller != request.user:
        messages.error(request, '您没有权限编辑此商品。')
        return redirect('items:item_detail', pk=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            images = request.FILES.getlist('images')
            for i, img in enumerate(images):
                item.images.create(image=img, is_primary=(i == 0 and not item.images.exists()))
            messages.success(request, '商品已更新！')
            return redirect('items:item_detail', pk=item.pk)
    else:
        form = ItemForm(instance=item)
    return render(request, 'items/item_form.html', {'form': form, 'action': '编辑', 'item': item})

@login_required
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if item.seller != request.user:
        messages.error(request, '您没有权限删除此商品。')
        return redirect('items:item_detail', pk=pk)
    if request.method == 'POST':
        item.status = 'removed'
        item.save()
        messages.success(request, '商品已下架。')
        return redirect('accounts:dashboard')
    return render(request, 'items/item_confirm_delete.html', {'item': item})

@login_required
def toggle_favorite(request, pk):
    item = get_object_or_404(Item, pk=pk)
    favorite = Favorite.objects.filter(user=request.user, item=item)
    if favorite.exists():
        favorite.delete()
        messages.info(request, '已取消收藏。')
    else:
        Favorite.objects.create(user=request.user, item=item)
        messages.success(request, '已收藏！')
    return redirect('items:item_detail', pk=item.pk)

@login_required
def messages_list(request):
    sent = Message.objects.filter(sender=request.user).select_related('receiver', 'item').order_by('-created_at')
    received = Message.objects.filter(receiver=request.user).select_related('sender', 'item').order_by('-created_at')
    # Mark received as read
    received.filter(is_read=False).update(is_read=True)
    return render(request, 'items/messages_list.html', {
        'sent': sent,
        'received': received,
    })
