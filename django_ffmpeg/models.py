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

from django_ffmpeg.defaults import *


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
    The directory name: 20190401/b9260873-b7dd-4995-a342-155b4abfafc8.mp4
    """
    name, ext = os.path.splitext(filename)
    # name = '%s_%s' % (datetime.datetime.now().strftime("%Y%m%d%H%M%S"), '{:05d}'.format(random.randint(0, 99999)))
    name = '%s_original' % str(uuid.uuid4())
    # directory = '%s/' % str(uuid.uuid4())
    directory = '%s/' % str(datetime.datetime.now().strftime("%Y%m%d"))

    return '%s%s%s' % (directory, name, ext.lower())


CONVERTING_COMMAND_MATCH_CHOICES = (
    ('extension', _('Extension')),
    ('name', _('File name')),
)

# class ConvertingCommand(models.Model):
#     '''
#     System commands for convertion videos to desired format
#     '''
#     match_by = models.CharField(
#         max_length=50,
#         verbose_name=_('Match by'),
#         choices=CONVERTING_COMMAND_MATCH_CHOICES,
#         default='extension',
#         help_text=_('Video param to detected from if this command should be used to convert given video'),
#     )
#     match_regex = models.CharField(
#         max_length=200,
#         verbose_name=_('RegExp to match video file'),
#     )
#     is_enabled = models.BooleanField(
#         verbose_name=_('Enabled?'),
#         default=True,
#     )
#     command = models.TextField(
#         verbose_name=_('System command to convert video'),
#         help_text='Example: /usr/bin/ffmpeg -nostats -y -i %(input_file)s -acodec libmp3lame -ar 44100 -f flv %(output_file)s',
#     )
#     convert_extension = models.CharField(
#         max_length=5,
#         verbose_name=_('Extension'),
#         help_text=_('Without dot: `.`'),
#     )
#     thumb_command = models.TextField(
#         verbose_name=_('System command to convert thumb'),
#         help_text='Example: /usr/bin/ffmpeg -hide_banner -nostats -i %(in_file)s -y -frames:v 1 -ss %(thumb_frame)s %(out_file)s',
#     )
#
#     def __unicode__(self):
#         return self.command[0:50]
#
#     class Meta:
#         verbose_name = _(u'Video convert command')
#         verbose_name_plural = _(u'Video convert commands')


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
    meta_info = models.TextField(
        verbose_name=_('Meta info about video'),
        null=True,
        editable=False,
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
    '''
    Uploaded video
    '''
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
        (1, _('Pending')),
        (2, _('Reviewed')),
    )
    revision = models.IntegerField(verbose_name=_('Revision status'), choices=revision_options, default=1)

    reason_options = (
        (1, _('Violence')),
        (2, _('Nudity')),
        (3, _('Hate')),
        (4, _('Other')),
        (5, _('Conversion error')),
    )
    reason = models.IntegerField(verbose_name=_('Reject reason'), choices=reason_options, default=4)

    other = models.CharField(verbose_name=_('Other reason'), max_length=2000, blank=True, default='')

    # @property
    # def converted_path(self):
    #     if not self.convert_extension:
    #         return None
    #     filepath = self.video.path
    #     filepath = filepath.replace(FFMPEG_ORIG_VIDEO, FFMPEG_CONV_VIDEO)
    #     return re.sub(r'[^\.]{1,10}$', self.convert_extension, filepath)
    #
    # @property
    # def converted_path_mov(self):
    #     filepath = self.video.path
    #     filepath = filepath.replace(FFMPEG_ORIG_VIDEO, FFMPEG_CONV_VIDEO)
    #     return re.sub(r'[^\.]{1,10}$', 'mov', filepath)
    #
    # @property
    # def converted_path_mp4(self):
    #     filepath = self.video.path
    #     filepath = filepath.replace(FFMPEG_ORIG_VIDEO, FFMPEG_CONV_VIDEO)
    #     return re.sub(r'[^\.]{1,10}$', 'mp4', filepath)
    #
    # @property
    # def thumb_video_path(self):
    #     filepath = self.video.path
    #     filepath = filepath.replace(FFMPEG_ORIG_VIDEO, FFMPEG_THUMB_VIDEO)
    #     return re.sub(r'[^\.]{1,10}$', 'jpg', filepath)

    def __unicode__(self):
        return self.title or u'Without title #%s' % self.pk

    class Meta:
        verbose_name = _('Review Video')
        verbose_name_plural = _('Review Videos')
