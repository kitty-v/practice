# Generated manually
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='余额'),
        ),
    ]
