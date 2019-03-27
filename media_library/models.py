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

    video_available = models.BooleanField(verbose_name=_('Video disponble'), default=False)

    format_set = GenericRelation(Format)


class Video_revision(models.Model):
    """ Almacena videos a revisar para aprobacion """
    # TODO revisar si se necesita algun campo mas
    create_date = models.DateTimeField(verbose_name=_('Fecha de creación'), auto_now_add=True)
    file = models.ForeignKey('Video', on_delete=models.CASCADE, blank=True, null=True,
                             related_name='video_rev')
    revision_options = (
        (1, 'Pendiente'),
        (2, 'Revisada'),
    )
    revision = models.IntegerField(verbose_name=_('Estado revisión'), choices=revision_options, default=1)

    status_options = (
        (1, 'Pendiente'),
        (2, 'Aprobado'),
        (3, 'Rechazado'),
    )
    status = models.IntegerField(verbose_name=_('Estatus'), choices=status_options, default=1)

    reason_options = (
        (1, 'Violencia'),
        (2, 'Desnudo'),
        (3, 'Odio'),
        (4, 'Otro'),
    )
    reason = models.IntegerField(verbose_name=_('Razón de rechazo'), choices=reason_options, default=1)

    other = models.CharField(verbose_name=_('Otra razón'), max_length=2000, blank=True, default='')

    class Meta:
        verbose_name = _('Revisión de video')
        verbose_name_plural = _('Revisión de videos')
        default_permissions = ('add', 'change', 'delete', 'view')