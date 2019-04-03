# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2019-04-01 04:17
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import cffmpeg.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ConvertVideo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=500, null=True, verbose_name='Title')),
                ('video', models.FileField(upload_to=cffmpeg.models.video_file_path, verbose_name='Video file')),
                ('thumb', models.ImageField(blank=True, null=True, upload_to=cffmpeg.models.thumb_file_path, verbose_name='Thumbnail image')),
                ('thumb_frame', models.PositiveIntegerField(default=0, verbose_name='Frame number for thumbnail')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created time')),
                ('meta_info', models.TextField(editable=False, null=True, verbose_name='Meta info about original video')),
                ('revision', models.IntegerField(choices=[(1, 'Pending'), (2, 'Reviewed')], default=1, verbose_name='Revision status')),
                ('reason', models.IntegerField(choices=[(1, 'Violence'), (2, 'Nudity'), (3, 'Hate'), (4, 'Other'), (5, 'Conversion error')], default=4, verbose_name='Reject reason')),
                ('other', models.CharField(blank=True, default=b'', max_length=2000, verbose_name='Other reason')),
            ],
            options={
                'verbose_name': 'Review Video',
                'verbose_name_plural': 'Review Videos',
            },
        ),
        migrations.CreateModel(
            name='EnqueuedVideo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('converted_video', models.FileField(null=True, upload_to=cffmpeg.models.video_file_path, verbose_name='Video file')),
                ('thumb', models.ImageField(blank=True, null=True, upload_to=cffmpeg.models.thumb_file_path, verbose_name='Thumbnail image')),
                ('thumb_frame', models.PositiveIntegerField(default=0, verbose_name='Frame number for thumbnail')),
                ('convert_status', models.CharField(choices=[(b'pending', 'Pending convert'), (b'started', 'Convert started'), (b'converted', 'Converted'), (b'error', 'Not converted due to error')], default=b'pending', max_length=16, verbose_name='MP4 Video conversion status')),
                ('converted_at', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='Convert time MP4')),
                ('last_convert_msg', models.TextField(blank=True, null=True, verbose_name='MP4 Message from last converting command')),
                ('meta_info', models.TextField(editable=False, null=True, verbose_name='Meta info about video')),
                ('convert_extension', models.CharField(editable=False, help_text='Without dot: `.`', max_length=5, null=True, verbose_name='Extension')),
                ('command', models.TextField(help_text=b'Example: /usr/bin/ffmpeg -nostats -y -i %(input_file)s -acodec libmp3lame -ar 44100 -f flv %(output_file)s', verbose_name='System command to convert video')),
                ('thumb_command', models.TextField(help_text=b'Example: /usr/bin/ffmpeg -hide_banner -nostats -i %(in_file)s -y -frames:v 1 -ss %(thumb_frame)s %(out_file)s', verbose_name='System command to convert thumb')),
            ],
            options={
                'verbose_name': 'Enqueued Video',
                'verbose_name_plural': 'Enqueued Videos',
            },
        ),
        migrations.AddField(
            model_name='convertvideo',
            name='enqueue',
            field=models.ManyToManyField(blank=True, default=None, related_name='enqueues', to='cffmpeg.EnqueuedVideo', verbose_name='Enqueued videos'),
        ),
        migrations.AddField(
            model_name='convertvideo',
            name='user',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Uploaded by'),
        ),
    ]
