# -*- coding: utf-8 -*-

# https://github.com/PixxxeL/django-ffmpeg/tree/master/django_ffmpeg
import time

from django.db.models.signals import post_save
from django.dispatch import receiver

from django_ffmpeg.converter import Converter
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
            video_enqueue = EnqueuedVideo.objects.create(convert_extension=format['extension'],
                                                         command=format['command'],
                                                         thumb_command=format['thumb_command'])
            # print "instance pk: %s" % instance.pk
            # instance.enqueue.add(video_enqueue)
            # instance.save()
            # print instance.enqueue.all()
            print "Iinstance pk: %s, Enqueing: %s" % (instance.pk, format['extension'])
            # start = time.time()
            # TODO this partially works:
            # enqueue(convert_video, instance.pk, video_enqueue.pk)
            # TODO testing with class
            n_instance = Converter()
            enqueue(n_instance.convert_video, instance.pk, video_enqueue.pk)

            # TODO not catching exceptions when bad video, check that

            # Converter().convert_instance(format, instance)
            # logger.info('Job finished at: %s s' % (time.time() - start))
            # print 'Job finished at: %s s' % (time.time() - start)

        pass  # write your code hier
    else:
        # print 'Progress:'
        # print instance.progress
        # print '----'
        pass
