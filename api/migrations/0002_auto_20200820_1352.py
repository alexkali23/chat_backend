# Generated by Django 3.1 on 2020-08-20 13:52

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messege_chat',
            name='created_date',
            field=models.DateTimeField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='messege_chat',
            name='update_date',
            field=models.DateTimeField(default=datetime.date.today),
        ),
    ]
