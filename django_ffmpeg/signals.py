# -*- coding: utf-8 -*-

# https://github.com/PixxxeL/django-ffmpeg/tree/master/django_ffmpeg
# TODO agregar señal al crear objeto
# TODO señal crea reporte de revision y encola conversion
# TODO en funcion de encolar hacer uso de python manage.py convert_videos y ConvertingCommand(match_by='name', match_regex='.*', command='/usr/bin/ffmpeg -hide_banner -nostats -i %(input_file)s -target film-dvd %(output_file)s', convert_extension='mp4').save()
# TODO se podria usar el modelo video del modulo para que funcione como reporte, al validar desde ahi o rechazar copiar archivo a Archivo_perfil y despues borrar
# TODO hacer que cree la version mp4 y mov
# TODO manejar error si se crea una pero no otra version
import time

from django.db.models.signals import post_save
from django.dispatch import receiver

from django_ffmpeg.task import convert_video
# from django_ffmpeg.utils import Converter

from django_ffmpeg.models import ConvertVideo, EnqueuedVideo
from media_library.models import Video_revision
import logging
from django_rq import enqueue

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ConvertVideo)
def format_post_save(sender, instance, created, **kwargs):
    if created:  # new object will be created
        print "New video uploaded..."
        FORMATS = [{'extension': 'mp4',
                    'command': '/usr/bin/ffmpeg -hide_banner -nostats -i %(input_file)s -target film-dvd %(output_file)s',
                    'thumb_command': '/usr/bin/ffmpeg -hide_banner -nostats -i %(in_file)s -y -frames:v 1 -ss %(thumb_frame)s %(out_file)s'},
                   {'extension': 'mov',
                    'command': '/usr/bin/ffmpeg -hide_banner -nostats -i %(input_file)s -target film-dvd %(output_file)s',
                    'thumb_command': '/usr/bin/ffmpeg -hide_banner -nostats -i %(in_file)s -y -frames:v 1 -ss %(thumb_frame)s %(out_file)s'}
                   ]
        for format in FORMATS:
             # TODO enqueue video no se relaciona con convertvideo, arreglar
             # TODO video se sube dos veces, arreglar
            video_enqueue = EnqueuedVideo.objects.create(convert_extension=format['extension'],
                                                         command=format['command'],
                                                         thumb_command=format['thumb_command'])
            print "instance pk: %s" % instance.pk
            # instance.enqueue.add(video_enqueue)
            # instance.save()
            # print instance.enqueue.all()
            print "Enqueing: %s" % format['extension']
            start = time.time()
            enqueue(convert_video, instance.pk, video_enqueue.pk)
            # Converter().convert_instance(format, instance)
            logger.info('Job finished at: %s s' % (time.time() - start))

        pass  # write your code hier
    else:
        # print 'Progress:'
        # print instance.progress
        print '----'
