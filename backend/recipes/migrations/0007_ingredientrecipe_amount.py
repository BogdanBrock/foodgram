# Generated by Django 3.2 on 2024-08-27 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_alter_shoppingcart_recipe'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredientrecipe',
            name='amount',
            field=models.PositiveSmallIntegerField(default=1),
            preserve_default=False,
        ),
    ]
