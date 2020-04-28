# Generated by Django 3.0.5 on 2020-04-28 06:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0007_applicant'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicant',
            name='status',
            field=models.CharField(choices=[('1', 'Accept'), ('2', 'Reject'), ('3', 'In Process')], default='In Process', max_length=10),
        ),
        migrations.AddField(
            model_name='userprofileinfo',
            name='full_name',
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AddField(
            model_name='userprofileinfo',
            name='skill_description',
            field=models.TextField(default=''),
        ),
    ]