# Generated by Django 5.0.7 on 2025-04-04 04:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommend', '0005_badge_userprofile_badges'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='dark_mode',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='last_active',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='notification_enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='points',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='badge',
            name='icon',
            field=models.ImageField(blank=True, null=True, upload_to='badges/'),
        ),
    ]
