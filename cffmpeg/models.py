# -*- coding: utf-8 -*-
import datetime
import os
import re
import uuid
from uuid import uuid4

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from cffmpeg.defaults import *


def filename_normalize(filename):
    ext = filename.split('.')[-1]
    return '%s.%s' % (uuid4().hex, ext)


def video_file_path(instance, filename):
    return '%s/%s/%s' % (FFMPEG_PRE_DIR, FFMPEG_ORIG_VIDEO, filename_normalize(filename),)


def thumb_file_path(instance, filename):
    return '%s/%s/%s' % (FFMPEG_PRE_DIR, FFMPEG_THUMB_VIDEO, filename_normalize(filename),)


def upload_reformat_name(instance, filename):
    """
    Format the name of the file consisting of the date, random number and extension
    The directory name: 20190401/o/b9260873-b7dd-4995-a342-155b4abfafc8.mp4
    """
    name, ext = os.path.splitext(filename)
    name = '%s' % str(uuid.uuid4())
    directory = '%s/o/' % str(datetime.datetime.now().strftime("%Y%m%d"))

    return '%s%s%s' % (directory, name, ext.lower())


CONVERTING_COMMAND_MATCH_CHOICES = (
    ('extension', _('Extension')),
    ('name', _('File name')),
)

VIDEO_CONVERSION_STATUS_CHOICES = (
    ('pending', _('Pending convert')),
    ('started', _('Convert started')),
    ('converted', _('Converted')),
    ('error', _('Not converted due to error')),
)


class EnqueuedVideo(models.Model):
    """ Video enqueued """
    converted_video = models.FileField(
        verbose_name=_('Converted Video file'),
        upload_to=video_file_path,
        null=True,
        blank=True
    )
    thumb = models.ImageField(
        verbose_name=_('Thumbnail image'),
        upload_to=thumb_file_path,
        null=True,
        blank=True,
    )
    thumb_frame = models.PositiveIntegerField(
        verbose_name=_('Frame number for thumbnail'),
        default=0,
        null=True,
        blank=True,
    )
    convert_status = models.CharField(
        max_length=16,
        verbose_name=_('Video conversion status'),
        choices=VIDEO_CONVERSION_STATUS_CHOICES,
        default='pending',
        null=True,
        blank=True,
    )
    converted_at = models.DateTimeField(
        verbose_name=_('Convert time'),
        editable=False,
        null=True,
        blank=True,
    )
    last_convert_msg = models.TextField(
        verbose_name=_('Message from last converting command'),
        null=True,
        blank=True,
    )
    full_convert_msg = models.TextField(
        verbose_name=_('Full Message from last converting command'),
        null=True,
        blank=True,
    )
    meta_info = models.TextField(
        verbose_name=_('Meta info about video'),
        null=True,
        editable=False,
        blank=True
    )
    convert_extension = models.CharField(
        max_length=5,
        verbose_name=_('Extension'),
        help_text=_('Without dot: `.`'),
        null=True,
        blank=True,
        editable=False,
    )
    command = models.TextField(
        verbose_name=_('System command to convert video'),
        help_text='Example: /usr/bin/ffmpeg -nostats -y -i %(input_file)s -acodec libmp3lame -ar 44100 -f flv %(output_file)s',
        null=True,
        blank=True,
    )
    thumb_command = models.TextField(
        verbose_name=_('System command to convert thumb'),
        help_text='Example: /usr/bin/ffmpeg -hide_banner -nostats -i %(in_file)s -y -frames:v 1 -ss %(thumb_frame)s %(out_file)s',
        null=True,
        blank=True,
    )

    def __unicode__(self):
        return 'pk: %s - %s' % (self.pk, self.convert_extension)

    class Meta:
        verbose_name = _('Enqueued Video')
        verbose_name_plural = _('Enqueued Videos')


class ConvertVideo(models.Model):
    """
    Uploaded video
    """
    title = models.CharField(
        max_length=500,
        verbose_name=_('Title'),
        null=True, blank=True,
    )
    video = models.FileField(
        verbose_name=_('Video file'),
        # upload_to=video_file_path,
        upload_to=upload_reformat_name,
    )

    enqueue = models.ManyToManyField(EnqueuedVideo, verbose_name=_('Enqueued videos'), blank=True, default=None,
                                     related_name='enqueues')

    thumb = models.ImageField(
        verbose_name=_('Thumbnail image'),
        upload_to=thumb_file_path,
        null=True, blank=True,
    )
    thumb_frame = models.PositiveIntegerField(
        verbose_name=_('Frame number for thumbnail'),
        default=0,
    )
    description = models.TextField(
        verbose_name=_('Description'),
        null=True, blank=True,
    )
    created_at = models.DateTimeField(
        verbose_name=_('Created time'),
        auto_now_add=True,
    )

    # TODO change user model
    user = models.ForeignKey(
        User,
        verbose_name=_('Uploaded by'),
        editable=False,
    )
    meta_info = models.TextField(
        verbose_name=_('Meta info about original video'),
        null=True,
        editable=False,
    )

    # For manual video validation
    revision_options = (
        ('pending', _('Pending')),
        ('reviewed', _('Reviewed')),
    )
    revision = models.CharField(verbose_name=_('Revision status'), choices=revision_options, default='pending',
                                max_length=16,
                                help_text=_('Set as reviewed if you are ok with everything in this page.'), )

    status_options = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    status = models.CharField(verbose_name=_('Acceptance status'), choices=status_options, default='pending',
                              max_length=16, help_text=_('Select the status of this review.'))

    reason_options = (
        ('violence', _('Violence')),
        ('nudity', _('Nudity')),
        ('hate', _('Hate')),
        ('other', _('Other')),
        ('conversion_error', _('Conversion error')),
    )
    reason = models.CharField(verbose_name=_('Reject reason'), choices=reason_options, default='other', max_length=16,
                              help_text=_('If select other, please fill the field below.'))

    other = models.CharField(verbose_name=_('Other reason'), max_length=2000, blank=True, default='')

    def __unicode__(self):
        return self.title or u'Without title #%s' % self.pk

    class Meta:
        verbose_name = _('Review Video')
        verbose_name_plural = _('Review Videos')
