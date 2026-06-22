# Generated manually
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('items', '0003_item_views'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='items.review', verbose_name='回复目标'),
        ),
    ]
