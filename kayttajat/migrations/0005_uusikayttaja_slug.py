# Generated by Django 5.2 on 2025-05-13 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kayttajat', '0004_delete_kayttaja'),
    ]

    operations = [
        migrations.AddField(
            model_name='uusikayttaja',
            name='slug',
            field=models.SlugField(default=''),
        ),
    ]
