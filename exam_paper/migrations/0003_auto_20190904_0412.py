# Generated by Django 2.2.4 on 2019-09-04 03:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam_paper', '0002_auto_20190904_0407'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examexternalreview',
            name='exam_paper',
            field=models.FileField(upload_to='exam_paper/external/exam_paper'),
        ),
        migrations.AlterField(
            model_name='examexternalreview',
            name='marking_scheme',
            field=models.FileField(upload_to='exam_paper/external/marking_scheme'),
        ),
    ]
