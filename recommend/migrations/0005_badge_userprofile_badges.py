# Generated by Django 5.0.7 on 2025-04-04 03:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommend', '0004_userprofile_completed_courses'),
    ]

    operations = [
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('icon', models.ImageField(upload_to='badges/')),
            ],
        ),
        migrations.AddField(
            model_name='userprofile',
            name='badges',
            field=models.ManyToManyField(blank=True, to='recommend.badge'),
        ),
    ]
