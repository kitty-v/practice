from django.conf import settings

def site_info(request):
    return {
        'SITE_NAME': '闲鱼集市',
        'SITE_DESCRIPTION': '安全便捷的二手物品交易平台',
    }
