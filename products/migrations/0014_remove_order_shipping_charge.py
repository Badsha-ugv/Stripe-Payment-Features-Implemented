# Generated by Django 5.1.4 on 2024-12-27 05:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0013_cart_shipping_address'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='shipping_charge',
        ),
    ]