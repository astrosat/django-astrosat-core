# Generated by Django 2.2 on 2019-08-20 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AstrosatSettings",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                )
            ],
            options={
                "verbose_name": "Astrosat Settings",
                "verbose_name_plural": "Astrosat Settings",
            },
        )
    ]
