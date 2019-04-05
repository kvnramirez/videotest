# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-05 19:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cffmpeg', '0002_enqueuedvideo_full_convert_msg'),
    ]

    operations = [
        migrations.AddField(
            model_name='convertvideo',
            name='status',
            field=models.IntegerField(choices=[(b'pending', b'Pending'), (b'approved', b'Approved'), (b'rejected', b'Rejected')], default=1, verbose_name='Acceptance status'),
        ),
        migrations.AlterField(
            model_name='convertvideo',
            name='reason',
            field=models.IntegerField(choices=[(1, 'Violence'), (2, 'Nudity'), (3, 'Hate'), (4, 'Other'), (5, 'Conversion error')], default=4, help_text='If select other, please fill the field below.', verbose_name='Reject reason'),
        ),
        migrations.AlterField(
            model_name='convertvideo',
            name='revision',
            field=models.IntegerField(choices=[(1, 'Pending'), (2, 'Reviewed')], default=1, help_text='Set as reviewed if you are ok with everything in this page.', verbose_name='Revision status'),
        ),
    ]
