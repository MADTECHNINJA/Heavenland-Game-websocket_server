# Generated by Django 4.0.4 on 2022-09-07 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_remove_charactermodel_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='GlobalGameSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_full_speed_spinner', models.BooleanField(default=False)),
                ('game_full_boomer', models.BooleanField(default=False)),
            ],
        ),
    ]
