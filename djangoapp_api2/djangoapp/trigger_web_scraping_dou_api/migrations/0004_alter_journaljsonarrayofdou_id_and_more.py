# Generated by Django 4.2.9 on 2024-01-12 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trigger_web_scraping_dou_api', '0003_journaljsonarrayofdou_id'),
    ]

    operations = [
         migrations.AlterField(
            model_name='journaljsonarrayofdou',
            name='urlTitle',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='journaljsonarrayofdou',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
