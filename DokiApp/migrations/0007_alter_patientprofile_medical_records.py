# Generated by Django 3.2.8 on 2021-11-11 04:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DokiApp', '0006_auto_20211111_0334'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patientprofile',
            name='medical_records',
            field=models.TextField(default='nothing yet'),
        ),
    ]