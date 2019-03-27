# -*- coding: utf-8 -*-
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import ugettext as _
from video_encoding.fields import VideoField
from video_encoding.models import Format


class Video(models.Model):
    width = models.PositiveIntegerField(
        editable=False,
        null=True,
    )
    height = models.PositiveIntegerField(
        editable=False,
        null=True,
    )
    duration = models.FloatField(
        editable=False,
        null=True,
    )

    file = VideoField(
        width_field='width',
        height_field='height',
        duration_field='duration',
    )

    video_available = models.BooleanField(verbose_name=_('Video available'), default=False)

    format_set = GenericRelation(Format)


class Video_revision(models.Model):
    """ Almacena videos a revisar para aprobacion """
    # TODO revisar si se necesita algun campo mas
    create_date = models.DateTimeField(verbose_name=_('Creation date'), auto_now_add=True)
    file = models.ForeignKey('Video', on_delete=models.CASCADE, blank=True, null=True,
                             related_name='video_rev')
    revision_options = (
        (1, 'Pending'),
        (2, 'Reviewed'),
    )
    revision = models.IntegerField(verbose_name=_('Revision date'), choices=revision_options, default=1)

    status_options = (
        (1, 'Pending'),
        (2, 'Approved'),
        (3, 'Rejected'),
    )
    status = models.IntegerField(verbose_name=_('Status'), choices=status_options, default=1)

    reason_options = (
        (1, 'Violence'),
        (2, 'Nudity'),
        (3, 'Hate'),
        (4, 'Other'),
    )
    reason = models.IntegerField(verbose_name=_('Reject reason'), choices=reason_options, default=1)

    other = models.CharField(verbose_name=_('Other reason'), max_length=2000, blank=True, default='')

    class Meta:
        verbose_name = _('Video review')
        verbose_name_plural = _('Videos review')
        default_permissions = ('add', 'change', 'delete', 'view')
