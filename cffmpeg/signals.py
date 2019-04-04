# -*- coding: utf-8 -*-
from django.db.models.signals import post_save
from django.dispatch import receiver

from cffmpeg.converter import Converter

from cffmpeg.models import ConvertVideo, EnqueuedVideo
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
            video_enqueue = EnqueuedVideo.objects.create(convert_extension=format['extension'],
                                                         command=format['command'],
                                                         thumb_command=format['thumb_command'])
            print "Iinstance pk: %s, Enqueing: %s" % (instance.pk, format['extension'])
            n_instance = Converter()
            enqueue(n_instance.convert_video, instance.pk, video_enqueue.pk)

        pass
    else:
        pass
