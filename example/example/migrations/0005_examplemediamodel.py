# Generated by Django 3.2.9 on 2022-08-09 10:42

from django.db import migrations, models
import example.models


class Migration(migrations.Migration):

    dependencies = [
        ('example', '0004_exampleconditionallydeletedthing'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExampleMediaModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('media', models.FileField(upload_to=example.models.example_media_path)),
            ],
        ),
    ]
