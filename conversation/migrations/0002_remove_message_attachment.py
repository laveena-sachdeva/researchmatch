# Generated by Django 3.0.5 on 2020-04-28 06:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('conversation', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='attachment',
        ),
    ]
