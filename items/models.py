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
            self.slug = slugify(self.name)
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
