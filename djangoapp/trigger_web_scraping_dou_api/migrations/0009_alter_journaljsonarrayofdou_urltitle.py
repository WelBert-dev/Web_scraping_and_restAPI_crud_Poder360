# Generated by Django 4.2.9 on 2024-01-19 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trigger_web_scraping_dou_api', '0008_alter_detailsinglejournalofdou_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journaljsonarrayofdou',
            name='urlTitle',
            field=models.CharField(unique=True),
        ),
    ]
