# Generated by Django 4.1.7 on 2023-03-15 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0009_allcollections_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='created_on',
            field=models.DateField(auto_now_add=True, verbose_name='created on'),
        ),
    ]
