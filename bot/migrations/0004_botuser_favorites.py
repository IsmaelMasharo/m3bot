# Generated by Django 3.0.5 on 2020-04-26 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0003_mxmtrack'),
    ]

    operations = [
        migrations.AddField(
            model_name='botuser',
            name='favorites',
            field=models.ManyToManyField(to='bot.MxmTrack'),
        ),
    ]
