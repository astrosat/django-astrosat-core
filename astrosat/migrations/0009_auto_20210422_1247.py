# Generated by Django 3.2 on 2021-04-22 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('astrosat', '0008_auto_20201118_1027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='astrosatsettings',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='databaselogrecord',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='databaselogtag',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
