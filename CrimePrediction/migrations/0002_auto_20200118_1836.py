# Generated by Django 3.0.2 on 2020-01-18 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CrimePrediction', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='description',
            field=models.TextField(max_length=600),
        ),
        migrations.AlterField(
            model_name='location',
            name='name',
            field=models.CharField(max_length=48),
        ),
    ]
