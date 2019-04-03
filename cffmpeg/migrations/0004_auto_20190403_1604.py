# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2019-04-03 16:04
from __future__ import unicode_literals

from django.db import migrations, models
import cffmpeg.models


class Migration(migrations.Migration):

    dependencies = [
        ('cffmpeg', '0003_auto_20190401_0446'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enqueuedvideo',
            name='converted_video',
            field=models.FileField(blank=True, null=True, upload_to=cffmpeg.models.video_file_path, verbose_name='Converted Video file'),
        ),
        migrations.AlterField(
            model_name='enqueuedvideo',
            name='meta_info',
            field=models.TextField(blank=True, editable=False, null=True, verbose_name='Meta info about video'),
        ),
    ]