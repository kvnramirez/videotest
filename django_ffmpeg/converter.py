# -*- coding: utf-8 -*-

import datetime
import logging
import os
import re

from django_ffmpeg.models import ConvertVideo, EnqueuedVideo
from pytz import timezone

logger = logging.getLogger(__name__)


class Converter(object):

    def convert_video(self, convert_video_id, enqueue_video_id):
        print "ConvertVideo pk: %s" % convert_video_id
        print "EnqueuedVideo pk: %s" % enqueue_video_id

        logger.info('ConvertVideo pk: %s' % convert_video_id)
        logger.info('EnqueuedVideo pk: %s' % enqueue_video_id)

        try:
            convert_video_object = ConvertVideo.objects.get(pk=convert_video_id)
        except ConvertVideo.DoesNotExist:
            logger.info('No original video found. Bypassing call...')
            return

        try:
            enqueue_video = EnqueuedVideo.objects.get(pk=enqueue_video_id)
        except EnqueuedVideo.DoesNotExist:
            logger.info('No enqueue video found. Bypassing call...')
            return

        convert_video_object.enqueue.add(enqueue_video)
        convert_video_object.save()

        video_extension = enqueue_video.convert_extension
        video_command = enqueue_video.command
        video_thumb_command = enqueue_video.thumb_command

        video = convert_video_object.video

        # enqueue video change status
        enqueue_video.convert_status = 'started'
        enqueue_video.save()

        # Choosing converting command
        filepath = video.path
        full_name = filepath.split('/')[-1]

        # video_info = {
        #     'name': full_name,
        #     'extension': full_name.split('.')[-1],
        # }

        if not video_command:
            logger.error('Conversion command not found...')
            enqueue_video.convert_status = 'error'
            enqueue_video.last_convert_msg = 'Conversion command not found'
            enqueue_video.save()
            return

        # logger.info('output video filepath: %s' % converted_path(video_extension, convert_video_object))
        print 'output video filepath: %s' % self.converted_path(video_extension, convert_video_object)

        try:
            c = video_command % {
                'input_file': filepath,
                'output_file': self.converted_path(video_extension, convert_video_object),
            }
            logger.info('Converting video command: %s' % c)
            print 'Converting video command: %s' % c
            output = self._cli(c)
            logger.info('Converting video result: %s' % output)
        except Exception as e:
            logger.error('Converting video error', exc_info=True)
            print 'Converting video error'
            print(e)
            enqueue_video.convert_status = 'error'
            enqueue_video.last_convert_msg = u'Exception while converting'
            enqueue_video.save()
            raise

        # logger.info('output thumb filepath: %s' % thumb_video_path(convert_video_object))
        print 'output thumb filepath: %s' % self.thumb_video_path(convert_video_object)

        # Convert thumb
        try:
            if not enqueue_video.thumb:
                cmd = video_thumb_command % {
                    'in_file': filepath,
                    'out_file': self.thumb_video_path(convert_video_object),
                    'thumb_frame': enqueue_video.thumb_frame,
                }
                self._cli(cmd, True)
                logger.info('Creating thumbnail command: %s' % cmd)
                print 'Creating thumbnail command: %s' % cmd
        except:
            logger.error('Converting thumb error', exc_info=True)
            print 'Converting thumb error'

        # logger.info('Success, video converted with extension: %s' % video_extension)
        print 'Success, video converted with extension: %s' % video_extension

        enqueue_video.convert_status = 'converted'
        enqueue_video.last_convert_msg = repr(output).replace('\\n', '\n').strip('\'')
        enqueue_video.converted_at = datetime.datetime.now(tz=timezone('UTC'))
        enqueue_video.converted_video.name = self.converted_path(video_extension, convert_video_object)
        enqueue_video.save()

    def converted_path(self, convert_extension, original_video):
        """
        Generate new path for converted video
        :param convert_extension: extension of output file
        :param original_video: original video object to extract filepath
        :return: new path to use
        """
        if not convert_extension:
            return None
        filepath = original_video.video.path
        # print "original converted filepath: %s" % filepath
        # print "replaced converted filepath: %s" % filepath.replace('_original', '_x264')
        replaced_filepath = filepath.replace('_original', '_x264')
        return re.sub(r'[^\.]{1,10}$', convert_extension, replaced_filepath)

    def thumb_video_path(self, original_video):
        """
        Generate new path for video thumbnail
        :param original_video: original video object to extract filepath
        :return: new path to use
        """
        filepath = original_video.video.path
        # print "original thumb filepath: %s" % filepath
        # print "replaced thumb filepath: %s" % filepath.replace('_original', '_thumb')
        replaced_filepath = filepath.replace('_original', '_thumb')
        return re.sub(r'[^\.]{1,10}$', 'jpg', replaced_filepath)

    def _cli(self, cmd, without_output=False):
        """
        Pass command to command line interface
        :param cmd: command to execute in command line interface
        :param without_output:
        :return: cli message output
        """
        if os.name == 'posix':
            import commands
            return commands.getoutput(cmd)
        else:
            import subprocess
            if without_output:
                DEVNULL = open(os.devnull, 'wb')
                subprocess.Popen(cmd, stdout=DEVNULL, stderr=DEVNULL)
            else:
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                return p.stdout.read()
