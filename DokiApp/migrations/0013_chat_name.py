# Generated by Django 3.2.9 on 2022-01-03 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DokiApp', '0012_chat_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='name',
            field=models.CharField(default='chat_name', max_length=32, unique=True),
        ),
    ]
