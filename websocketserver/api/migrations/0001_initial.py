# Generated by Django 4.0.4 on 2022-06-10 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(db_index=True, max_length=32)),
                ('building_id', models.CharField(max_length=64)),
                ('elevation', models.DecimalField(decimal_places=12, max_digits=20)),
                ('scale', models.DecimalField(decimal_places=12, max_digits=20)),
                ('rotation', models.DecimalField(decimal_places=12, max_digits=20)),
            ],
        ),
    ]
