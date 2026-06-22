from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField('手机号', max_length=20, blank=True)
    avatar = models.ImageField('头像', upload_to='avatars/', blank=True, null=True)
    balance = models.DecimalField('余额', max_digits=10, decimal_places=2, default=0.00)
    bio = models.TextField('个人简介', max_length=500, blank=True)
    province = models.CharField('省份', max_length=30, blank=True)
    city = models.CharField('城市', max_length=30, blank=True)
    district = models.CharField('区/县', max_length=30, blank=True)
    street_address = models.CharField('详细地址', max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'

    def __str__(self):
        return f'{self.user.username}的资料'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
