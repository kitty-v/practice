from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField('分类名称', max_length=50)
    slug = models.SlugField('标识', max_length=50, unique=True, blank=True)
    icon = models.CharField('图标(Emoji)', max_length=10, default='📦')
    order = models.IntegerField('排序', default=0)

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Item(models.Model):
    CONDITION_CHOICES = [
        ('new', '全新'),
        ('like_new', '几乎全新'),
        ('good', '良好'),
        ('fair', '一般'),
        ('poor', '较差'),
    ]
    STATUS_CHOICES = [
        ('active', '在售'),
        ('sold', '已售'),
        ('removed', '已下架'),
    ]

    title = models.CharField('标题', max_length=100)
    description = models.TextField('描述', max_length=2000)
    price = models.DecimalField('价格', max_digits=10, decimal_places=2)
    condition = models.CharField('成色', max_length=10, choices=CONDITION_CHOICES, default='good')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name='分类', related_name='items')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='卖家', related_name='items')
    status = models.CharField('状态', max_length=10, choices=STATUS_CHOICES, default='active')
    views = models.PositiveIntegerField('浏览量', default=0)
    stock = models.PositiveIntegerField('库存', default=1)
    sold_count = models.PositiveIntegerField('已售', default=0)
    created_at = models.DateTimeField('发布时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def primary_image(self):
        img = self.images.filter(is_primary=True).first()
        if img:
            return img.image.url
        first = self.images.first()
        if first:
            return first.image.url
        return None

class ItemImage(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='images', verbose_name='商品')
    image = models.ImageField('图片', upload_to='items/')
    is_primary = models.BooleanField('主图', default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '商品图片'
        verbose_name_plural = '商品图片'

    def __str__(self):
        return f'{self.item.title} - 图片'

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name='用户')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='favorites', verbose_name='商品')
    created_at = models.DateTimeField('收藏时间', auto_now_add=True)

    class Meta:
        verbose_name = '收藏'
        verbose_name_plural = '收藏'
        unique_together = ('user', 'item')

    def __str__(self):
        return f'{self.user.username}收藏了{self.item.title}'

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name='发送者')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', verbose_name='接收者')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='messages', verbose_name='关联商品', null=True, blank=True)
    content = models.TextField('内容', max_length=2000)
    is_read = models.BooleanField('已读', default=False)
    created_at = models.DateTimeField('发送时间', auto_now_add=True)

    class Meta:
        verbose_name = '消息'
        verbose_name_plural = '消息'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.sender.username} -> {self.receiver.username}: {self.content[:20]}'

class Review(models.Model):
    RATING_CHOICES = [(i, f'{i} 星') for i in range(1, 6)]

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='reviews', verbose_name='关联商品')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given', verbose_name='评价人')
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received', verbose_name='被评价人')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name='回复目标')
    rating = models.PositiveSmallIntegerField('评分', choices=RATING_CHOICES, default=5)
    comment = models.TextField('评价内容', max_length=500, blank=True)
    created_at = models.DateTimeField('评价时间', auto_now_add=True)

    class Meta:
        verbose_name = '评价'
        verbose_name_plural = '评价'
        ordering = ['-created_at']
        # unique_together = ('item', 'reviewer', 'reviewee')  # removed so seller can reply multiple times

    def __str__(self):
        return f'{self.reviewer.username} 对 {self.reviewee.username} 的评价（{self.rating}星）'


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', '待付款'),
        ('paid', '已付款'),
        ('shipped', '已发货'),
        ('completed', '已完成'),
        ('refund_requested', '申请退款'),
        ('refunded', '已退款'),
        ('cancelled', '已取消'),
    ]
    TRANSACTION_CHOICES = [
        ('online', '线上交易'),
        ('offline', '线下交易'),
    ]

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_as_buyer', verbose_name='买家')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_as_seller', verbose_name='卖家')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='orders', verbose_name='商品')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_type = models.CharField('交易方式', max_length=10, choices=TRANSACTION_CHOICES, default='online')
    quantity = models.PositiveIntegerField('数量', default=1)
    amount = models.DecimalField('金额', max_digits=10, decimal_places=2)
    tracking_company = models.CharField('快递公司', max_length=50, blank=True)
    tracking_number = models.CharField('运单号', max_length=100, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.buyer.username} x {self.item.title} ({self.get_status_display()})'

class RevenueRecord(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='revenue_records', verbose_name='卖家')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='revenue_records', verbose_name='关联订单')
    amount = models.DecimalField('金额', max_digits=10, decimal_places=2)
    created_at = models.DateTimeField('记录时间', auto_now_add=True)

    class Meta:
        verbose_name = '收益记录'
        verbose_name_plural = '收益记录'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.seller.username} +¥{self.amount}'
