# Generated by Django 4.2.9 on 2024-01-19 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trigger_web_scraping_dou_api', '0007_alter_detailsinglejournalofdou_versao_certificada'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detailsinglejournalofdou',
            name='title',
            field=models.CharField(unique=False),
        ),
    ]