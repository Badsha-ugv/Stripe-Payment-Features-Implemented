# Generated by Django 5.1.4 on 2024-12-26 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_shippingaddress_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='shippingaddress',
            name='inside_dhaka',
            field=models.BooleanField(default=True),
        ),
    ]
