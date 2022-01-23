# Generated by Django 3.2.9 on 2022-01-22 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DokiApp', '0021_alter_rate_rate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rate',
            name='rate',
            field=models.PositiveSmallIntegerField(choices=[(0, '0'), (1, '*'), (2, '**'), (3, '***'), (4, '****'), (5, '*****')], default=0),
        ),
        migrations.AlterField(
            model_name='reserve',
            name='time',
            field=models.CharField(choices=[('AM', 'Before 12'), ('PM', 'After 12')], default='AM', max_length=2),
        ),
    ]