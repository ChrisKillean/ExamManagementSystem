# Generated by Django 2.2.4 on 2019-09-04 03:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam_paper', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examexternalreview',
            name='exam_paper',
            field=models.FileField(upload_to='external/exam_paper'),
        ),
        migrations.AlterField(
            model_name='examexternalreview',
            name='marking_scheme',
            field=models.FileField(upload_to='external/marking_scheme'),
        ),
    ]
