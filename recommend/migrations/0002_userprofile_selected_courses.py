# Generated by Django 5.0.7 on 2025-03-05 03:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommend', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='selected_courses',
            field=models.ManyToManyField(blank=True, to='recommend.course'),
        ),
    ]
