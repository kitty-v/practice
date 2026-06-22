# Generated manually
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('items', '0004_review_parent'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', '待付款'), ('paid', '已付款'), ('shipped', '已发货'), ('completed', '已完成'), ('refund_requested', '申请退款'), ('refunded', '已退款')], default='pending', max_length=20, verbose_name='状态')),
                ('transaction_type', models.CharField(choices=[('online', '线上交易'), ('offline', '线下交易')], default='online', max_length=10, verbose_name='交易方式')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='金额')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders_as_buyer', to='auth.user', verbose_name='买家')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='items.item', verbose_name='商品')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders_as_seller', to='auth.user', verbose_name='卖家')),
            ],
            options={
                'verbose_name': '订单',
                'verbose_name_plural': '订单',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='RevenueRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='金额')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='记录时间')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='revenue_records', to='items.order', verbose_name='关联订单')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='revenue_records', to='auth.user', verbose_name='卖家')),
            ],
            options={
                'verbose_name': '收益记录',
                'verbose_name_plural': '收益记录',
                'ordering': ['-created_at'],
            },
        ),
    ]
