# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2019-04-01 03:24
from __future__ import unicode_literals

from django.db import migrations, models
import django_ffmpeg.models


class Migration(migrations.Migration):

    dependencies = [
        ('django_ffmpeg', '0003_auto_20190401_0306'),
    ]

    operations = [
        migrations.AddField(
            model_name='convertvideo',
            name='convert_extension_2',
            field=models.CharField(editable=False, help_text='Without dot: `.`', max_length=5, null=True, verbose_name='Extension 2'),
        ),
        migrations.AlterField(
            model_name='convertvideo',
            name='last_convert_msg',
            field=models.TextField(blank=True, null=True, verbose_name='MP4 Message from last converting command'),
        ),
        migrations.AlterField(
            model_name='convertvideo',
            name='last_convert_msg_mov',
            field=models.TextField(blank=True, null=True, verbose_name='MOV Message from last converting command'),
        ),
        migrations.AlterField(
            model_name='convertvideo',
            name='output_video_mov',
            field=models.FileField(blank=True, null=True, upload_to=django_ffmpeg.models.video_file_path, verbose_name='MOV Video file'),
        ),
        migrations.AlterField(
            model_name='convertvideo',
            name='output_video_mp4',
            field=models.FileField(blank=True, null=True, upload_to=django_ffmpeg.models.video_file_path, verbose_name='MP4 Video file'),
        ),
    ]
