# Generated by Django 2.2.6 on 2022-05-31 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_auto_20220516_1619'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(unique=True, verbose_name='hjdfhfsjk'),
        ),
    ]
