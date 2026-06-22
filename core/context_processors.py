from django.conf import settings
from django.db import models
from items.models import Message, RevenueRecord

def site_info(request):
    ctx = {
        'SITE_NAME': '冶金跳蚤市场',
        'SITE_DESCRIPTION': '旧物回炉，好物重铸',
    }
    if request.user.is_authenticated:
        ctx['unread_count'] = Message.objects.filter(receiver=request.user, is_read=False).count()
        try:
            ctx['user_balance'] = request.user.profile.balance
            rev = RevenueRecord.objects.filter(seller=request.user).aggregate(total=models.Sum('amount'))
            ctx['total_revenue'] = rev['total'] or 0
        except:
            ctx['user_balance'] = 0
            ctx['total_revenue'] = 0
    return ctx
