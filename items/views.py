from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, F
from django.db import transaction
from .models import Item, Category, Favorite, Message, Review, Order, RevenueRecord
from .forms import ItemForm, MessageForm, ReviewForm

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


def hot_items(request):
    items = Item.objects.filter(status='active').select_related('seller', 'category').order_by('-views', '-created_at')
    return render(request, 'items/item_list.html', {
        'items': items,
        'categories': Category.objects.all(),
        'hot_mode': True,
    })

def item_detail(request, pk):
    item = get_object_or_404(Item.objects.select_related('seller', 'category'), pk=pk)
    Item.objects.filter(pk=item.pk).update(views=F('views') + 1)
    item.refresh_from_db()
    images = item.images.all()
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, item=item).exists()

    related_items = Item.objects.filter(
        category=item.category, status='active'
    ).exclude(pk=item.pk)[:4]

    # --- Reviews for this item ---
    seller_reviews = Review.objects.filter(item=item, reviewee=item.seller).select_related('reviewer')
    seller_given_reviews = Review.objects.filter(item=item, reviewer=item.seller).select_related('reviewee')
    # Build review threads: group seller replies under their parent review
    review_threads = []
    buyer_reviews = Review.objects.filter(item=item, reviewee=item.seller, parent__isnull=True).select_related('reviewer')
    for br in buyer_reviews:
        replies = Review.objects.filter(item=item, parent=br).select_related('reviewer')
        reply_count = replies.count()
        review_threads.append({'review': br, 'replies': replies, 'reply_count': reply_count})
    review_form = ReviewForm()
    my_review_of_seller = None
    has_contacted_seller = False
    buyers_to_review = []

    if request.user.is_authenticated:
        if request.user != item.seller:
            has_contacted_seller = Message.objects.filter(
                item=item, sender=request.user, receiver=item.seller
            ).exists()
            my_review_of_seller = Review.objects.filter(
                item=item, reviewer=request.user, reviewee=item.seller
            ).first()
            if my_review_of_seller:
                review_form = ReviewForm(instance=my_review_of_seller)
        else:
            buyers = User.objects.filter(
                Q(sent_messages__item=item, sent_messages__receiver=item.seller) |
                Q(received_messages__item=item, received_messages__sender=item.seller)
            ).exclude(pk=item.seller.pk).distinct()
            for buyer in buyers:
                buyer_reviews = Review.objects.filter(item=item, reviewer=buyer, reviewee=item.seller).order_by('-created_at')
                for br in buyer_reviews:
                    buyers_to_review.append({
                        'buyer': buyer,
                        'review': br,
                    })

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
        'review_threads': review_threads,
        'review_form': review_form,
        'my_review_of_seller': my_review_of_seller,
        'has_contacted_seller': has_contacted_seller,
        'buyers_to_review': buyers_to_review,
    })

@login_required

@login_required
@transaction.atomic
def buy_item(request, pk):
    """创建订单（买家发起购买）"""
    item = get_object_or_404(
        Item.objects.select_for_update().select_related('seller'),
        pk=pk
    )
    if request.user == item.seller:
        messages.error(request, '不能购买自己的商品')
        return redirect('items:item_detail', pk=pk)
    if item.status != 'active':
        messages.error(request, '该商品已下架或售出')
        return redirect('items:item_detail', pk=pk)

    # Get quantity
    try:
        quantity = int(request.POST.get('quantity', '1'))
    except ValueError:
        quantity = 1
    if quantity < 1:
        quantity = 1
    if item.stock < quantity:
        messages.error(request, f'库存不足，当前仅剩 {item.stock} 件')
        return redirect('items:item_detail', pk=pk)

    total_amount = item.price * quantity
    transaction_type = request.POST.get('transaction_type', 'online')

    order = Order.objects.create(
        buyer=request.user,
        seller=item.seller,
        item=item,
        quantity=quantity,
        transaction_type=transaction_type,
        amount=total_amount,
    )

    if transaction_type == 'online':
        # Deduct from buyer balance immediately (escrow)
        profile = request.user.profile
        if profile.balance < total_amount:
            order.delete()
            messages.error(request, '余额不足，请先充值')
            return redirect('accounts:balance')
        profile.balance -= total_amount
        profile.save(update_fields=['balance'])
        order.status = 'paid'
        order.save(update_fields=['status'])
        messages.success(request, f'购买成功！款项已冻结，确认收货后到账卖家')
    else:
        messages.success(request, '订单已创建，请联系卖家完成线下交易')

    # Decrement stock
    item.stock -= quantity
    item.sold_count += quantity
    if item.stock == 0:
        item.status = 'sold'
    item.save(update_fields=['stock', 'sold_count', 'status'])

    return redirect('items:order_detail', pk=order.pk)

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.select_related('buyer', 'seller', 'item', 'item__category'), pk=pk)
    if request.user not in (order.buyer, order.seller):
        messages.error(request, '无权查看此订单')
        return redirect('core:home')
    return render(request, 'items/order_detail.html', {'order': order})

@login_required
def order_ship(request, pk):
    """卖家确认发货（填写运单号）"""
    order = get_object_or_404(Order, pk=pk)
    if request.user != order.seller:
        messages.error(request, '无权操作')
        return redirect('core:home')
    if order.status != 'paid':
        messages.error(request, '当前状态不能发货')
        return redirect('items:order_detail', pk=pk)

    order.tracking_company = request.POST.get('tracking_company', '').strip()
    order.tracking_number = request.POST.get('tracking_number', '').strip()
    if not order.tracking_number:
        messages.error(request, '请填写运单号')
        return redirect('items:order_detail', pk=pk)

    order.status = 'shipped'
    order.save(update_fields=['status', 'tracking_company', 'tracking_number'])
    messages.success(request, '已标记为已发货，运单号已通知买家')
    return redirect('items:order_detail', pk=pk)

@login_required
def order_offline(request, pk):
    """卖家标记为线下交易完成"""
    order = get_object_or_404(Order, pk=pk)
    if request.user != order.seller:
        messages.error(request, '无权操作')
        return redirect('core:home')
    if order.status != 'paid':
        messages.error(request, '当前状态不能操作')
        return redirect('items:order_detail', pk=pk)
    order.status = 'shipped'
    order.save(update_fields=['status'])
    messages.success(request, '已标记为线下交易，等待买家确认')
    return redirect('items:order_detail', pk=pk)

@login_required
def order_confirm(request, pk):
    """买家确认收货 → 钱到卖家"""
    order = get_object_or_404(Order.objects.select_related('seller'), pk=pk)
    if request.user != order.buyer:
        messages.error(request, '无权操作')
        return redirect('core:home')
    if order.status not in ('paid', 'shipped'):
        messages.error(request, '当前状态不能确认收货')
        return redirect('items:order_detail', pk=pk)

    # Release funds to seller
    seller_profile = order.seller.profile
    seller_profile.balance += order.amount
    seller_profile.save(update_fields=['balance'])

    # Record revenue
    RevenueRecord.objects.create(seller=order.seller, order=order, amount=order.amount)

    order.status = 'completed'
    order.save(update_fields=['status'])
    messages.success(request, '已确认收货，款项已到账卖家')
    return redirect('items:order_detail', pk=pk)


@login_required
def order_cancel(request, pk):
    """买家取消待付款订单"""
    order = get_object_or_404(Order.objects.select_related('item'), pk=pk)
    if request.user != order.buyer:
        messages.error(request, '无权操作')
        return redirect('core:home')
    if order.status != 'pending':
        messages.error(request, '当前状态不能取消')
        return redirect('items:order_detail', pk=pk)

    # Restock
    item = order.item
    item.stock += order.quantity
    item.sold_count -= order.quantity
    if item.status == 'sold' and item.stock > 0:
        item.status = 'active'
    item.save(update_fields=['stock', 'sold_count', 'status'])

    order.status = 'cancelled'
    order.save(update_fields=['status'])
    messages.success(request, '订单已取消')
    return redirect('accounts:dashboard')

@login_required
def order_refund_request(request, pk):
    """买家申请退款"""
    order = get_object_or_404(Order, pk=pk)
    if request.user != order.buyer:
        messages.error(request, '无权操作')
        return redirect('core:home')
    if order.status not in ('paid', 'shipped'):
        messages.error(request, '当前状态不能申请退款')
        return redirect('items:order_detail', pk=pk)
    order.status = 'refund_requested'
    order.save(update_fields=['status'])
    messages.success(request, '退款申请已提交，等待卖家处理')
    return redirect('items:order_detail', pk=pk)

@login_required
def order_refund_approve(request, pk):
    """卖家同意退款 → 钱退回买家"""
    order = get_object_or_404(Order.objects.select_related('buyer', 'item'), pk=pk)
    if request.user != order.seller:
        messages.error(request, '无权操作')
        return redirect('core:home')
    if order.status != 'refund_requested':
        messages.error(request, '当前状态不能退款')
        return redirect('items:order_detail', pk=pk)

    # Return funds to buyer
    buyer_profile = order.buyer.profile
    buyer_profile.balance += order.amount
    buyer_profile.save(update_fields=['balance'])

    # Restock
    item = order.item
    item.stock += order.quantity
    item.sold_count -= order.quantity
    if item.status == 'sold' and item.stock > 0:
        item.status = 'active'
    item.save(update_fields=['stock', 'sold_count', 'status'])

    order.status = 'refunded'
    order.save(update_fields=['status'])
    messages.success(request, '已退款，款项已退回买家')
    return redirect('items:order_detail', pk=pk)



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
            if images:
                # 用户上传了新图片 → 删除旧图片，用新图片替换
                item.images.all().delete()
                for i, img in enumerate(images):
                    item.images.create(image=img, is_primary=(i == 0))
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
        if item.status == 'removed':
            # Permanently delete
            item.delete()
            messages.success(request, '商品已永久删除。')
            return redirect('accounts:dashboard')
        else:
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
    user = request.user
    all_msgs = Message.objects.filter(
        Q(sender=user) | Q(receiver=user)
    ).select_related('sender', 'receiver', 'item').order_by('created_at')

    # Group every message into a conversation keyed by "the other person",
    # so sent and received messages interleave in one continuous thread.
    conversations = {}
    for msg in all_msgs:
        partner = msg.receiver if msg.sender_id == user.id else msg.sender
        conv = conversations.setdefault(partner.id, {'partner': partner, 'messages': [], 'unread': 0})
        conv['messages'].append(msg)
        if msg.receiver_id == user.id and not msg.is_read:
            conv['unread'] += 1

    conversation_list = sorted(conversations.values(), key=lambda c: c['messages'][-1].created_at, reverse=True)
    for conv in conversation_list:
        conv['last'] = conv['messages'][-1]

    active_id = request.GET.get('with', '')
    active_conv = conversations.get(int(active_id)) if active_id.isdigit() else None
    if not active_conv and conversation_list:
        active_conv = conversation_list[0]

    if active_conv:
        Message.objects.filter(sender=active_conv['partner'], receiver=user, is_read=False).update(is_read=True)
        active_conv['unread'] = 0

    return render(request, 'items/messages_list.html', {
        'conversation_list': conversation_list,
        'active_conv': active_conv,
    })

@login_required
def reply_message(request):
    receiver_id = request.POST.get('receiver_id')
    if request.method == 'POST':
        receiver = get_object_or_404(User, pk=receiver_id)
        item_id = request.POST.get('item_id')
        item = Item.objects.filter(pk=item_id).first() if item_id else None
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(sender=request.user, receiver=receiver, item=item, content=content)
        else:
            messages.error(request, '回复内容不能为空。')
    return redirect(f"{reverse('items:messages_list')}?with={receiver_id}")

@login_required
def leave_review(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method != 'POST':
        return redirect('items:item_detail', pk=pk)

    target = get_object_or_404(User, pk=request.POST.get('target_id'))
    reviewer = request.user

    if target == reviewer:
        messages.error(request, '不能评价自己。')
        return redirect('items:item_detail', pk=pk)

    # 只允许针对该商品的买卖双方互评（reviewer 与 target 中必须有一方是卖家）
    if reviewer != item.seller and target != item.seller:
        messages.error(request, '只能评价与该商品交易相关的买家或卖家。')
        return redirect('items:item_detail', pk=pk)

    # 卖家评价买家：buyers_to_review 已确保有交互，直接放行
    if reviewer != item.seller:
        # 非卖家评价必须双方有过站内消息
        has_interacted = Message.objects.filter(
            item=item, sender=reviewer, receiver=target
        ).exists() or Message.objects.filter(
            item=item, sender=target, receiver=reviewer
        ).exists()
        if not has_interacted:
            messages.error(request, '需要先联系过对方，才能发表评价。')
            return redirect('items:item_detail', pk=pk)

    form = ReviewForm(request.POST)
    if form.is_valid():
        parent_id = request.POST.get('parent_id')
        parent = Review.objects.filter(pk=parent_id).first() if parent_id else None
        Review.objects.create(
            item=item, reviewer=reviewer, reviewee=target,
            parent=parent,
            rating=form.cleaned_data['rating'],
            comment=form.cleaned_data['comment'],
        )
        messages.success(request, '评价已提交！')
    else:
        messages.error(request, '评价提交失败：' + str(form.errors))
    return redirect('items:item_detail', pk=pk)
