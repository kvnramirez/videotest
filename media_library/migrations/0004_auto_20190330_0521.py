# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2019-03-30 05:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media_library', '0003_auto_20190327_1813'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='video_mov',
            field=models.FileField(blank=True, default=b'', upload_to=b''),
        ),
        migrations.AddField(
            model_name='video',
            name='video_mp4',
            field=models.FileField(blank=True, default=b'', upload_to=b''),
        ),
        migrations.AddField(
            model_name='video_revision',
            name='conversion_error_msg',
            field=models.CharField(blank=True, default=b'', max_length=2000, verbose_name='Conversion error msg'),
        ),
        migrations.AddField(
            model_name='video_revision',
            name='visible',
            field=models.BooleanField(default=False, verbose_name='Is visible?'),
        ),
        migrations.AlterField(
            model_name='video_revision',
            name='reason',
            field=models.IntegerField(choices=[(1, b'Violence'), (2, b'Nudity'), (3, b'Hate'), (4, b'Other'), (5, b'Conversion error')], default=1, verbose_name='Reject reason'),
        ),
        migrations.AlterField(
            model_name='video_revision',
            name='revision',
            field=models.IntegerField(choices=[(1, b'Pending'), (2, b'Reviewed')], default=1, verbose_name='Revision status'),
        ),
        migrations.AlterField(
            model_name='video_revision',
            name='status',
            field=models.IntegerField(choices=[(1, b'Pending'), (2, b'Approved'), (3, b'Rejected'), (4, b'Error')], default=1, verbose_name='Status'),
        ),
    ]