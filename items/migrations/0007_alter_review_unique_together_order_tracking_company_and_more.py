from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0006_alter_review_unique_together_item_sold_count_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='tracking_company',
            field=models.CharField(blank=True, max_length=50, verbose_name='快递公司'),
        ),
        migrations.AddField(
            model_name='order',
            name='tracking_number',
            field=models.CharField(blank=True, max_length=100, verbose_name='运单号'),
        ),
    ]
