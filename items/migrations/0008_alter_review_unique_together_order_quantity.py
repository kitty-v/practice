from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0007_alter_review_unique_together_order_tracking_company_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='quantity',
            field=models.PositiveIntegerField(default=1, verbose_name='数量'),
        ),
    ]
