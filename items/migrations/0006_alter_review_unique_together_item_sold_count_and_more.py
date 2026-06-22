from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0005_order_revenuerecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='sold_count',
            field=models.PositiveIntegerField(default=0, verbose_name='已售'),
        ),
        migrations.AddField(
            model_name='item',
            name='stock',
            field=models.PositiveIntegerField(default=1, verbose_name='库存'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', '待付款'), ('paid', '已付款'), ('shipped', '已发货'), ('completed', '已完成'), ('refund_requested', '申请退款'), ('refunded', '已退款'), ('cancelled', '已取消')], default='pending', max_length=20, verbose_name='状态'),
        ),
    ]
