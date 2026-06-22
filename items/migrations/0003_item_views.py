# Generated manually
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('items', '0002_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='views',
            field=models.PositiveIntegerField('浏览量', default=0),
        ),
    ]
