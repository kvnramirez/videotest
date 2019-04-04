# -*- coding: utf-8 -*-

import datetime
import errno
import logging
import os
import re
import traceback

from cffmpeg.defaults import CONVERTER_ORIGINAL_FOLDER, CONVERTER_COVERTED_FOLDER, CONVERTER_THUMB_FOLDER
from cffmpeg.models import ConvertVideo, EnqueuedVideo
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
            enqueue_video.last_convert_msg = u'Conversion command not found'
            enqueue_video.full_convert_msg = u'No input command to pass to ffmpeg'
            enqueue_video.save()
            return

        # logger.info('output video filepath: %s' % converted_path(video_extension, convert_video_object))
        print 'output video filepath: %s' % self.converted_path(video_extension, convert_video_object)

        stderrdata = None
        try:
            c = video_command % {
                'input_file': filepath,
                'output_file': self.converted_path(video_extension, convert_video_object),
            }
            logger.info('Converting video command: %s' % c)
            print 'Converting video command: %s' % c
            stdoutdata, stderrdata, errors = self._cli(c)
            logger.info('Converting video result: %s' % stderrdata)
        except Exception as e:
            logger.error('Converting video error', exc_info=True)
            print 'Converting video error'
            print(e)
            enqueue_video.convert_status = 'error'
            enqueue_video.last_convert_msg = u'Error while converting'
            enqueue_video.full_convert_msg = stderrdata
            enqueue_video.save()
            raise

        # logger.info('output thumb filepath: %s' % thumb_video_path(convert_video_object))
        print 'output thumb filepath: %s' % self.thumb_video_path(convert_video_object)

        thumb_errors = False
        thumb_stderrdata = None
        # Convert thumb
        try:
            if not enqueue_video.thumb:
                cmd = video_thumb_command % {
                    'in_file': filepath,
                    'out_file': self.thumb_video_path(convert_video_object),
                    'thumb_frame': enqueue_video.thumb_frame,
                }
                thumb_stdoutdata, thumb_stderrdata, thumb_errors = self._cli(cmd, True)
                logger.info('Creating thumbnail command: %s' % cmd)
                print 'Creating thumbnail command: %s' % cmd
        except:
            logger.error('Converting thumb error', exc_info=True)
            print 'Converting thumb error'

        # logger.info('Success, video converted with extension: %s' % video_extension)
        print 'Success, video converted with extension: %s' % video_extension

        print 'thumb_stderrdata: '
        print thumb_stderrdata
        print 'thumb_errors: '
        print thumb_errors

        if not thumb_errors:
            enqueue_video.thumb.name = self.thumb_video_path(convert_video_object)

        print 'stderrdata: '
        print stderrdata

        enqueue_video.convert_status = 'converted'
        # enqueue_video.last_convert_msg = repr(stderrdata).replace('\\n', '\n').strip('\'')
        enqueue_video.last_convert_msg = u'Video convert successfully'
        enqueue_video.full_convert_msg = stderrdata
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
        replaced_filepath = filepath.replace(CONVERTER_ORIGINAL_FOLDER, CONVERTER_COVERTED_FOLDER)
        directory = os.path.dirname(replaced_filepath)
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
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
        replaced_filepath = filepath.replace(CONVERTER_ORIGINAL_FOLDER, CONVERTER_THUMB_FOLDER)
        directory = os.path.dirname(replaced_filepath)
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        return re.sub(r'[^\.]{1,10}$', 'jpg', replaced_filepath)

    # https://stackoverflow.com/questions/2502833/store-output-of-subprocess-popen-call-in-a-string
    # https://stackoverflow.com/questions/40625862/python-subprocess-popen-no-such-file-or-directory/40626107
    # https://stackoverflow.com/questions/47414122/ffmpeg-not-working-from-python-subprocess-popen-but-works-from-command-line
    # https://stackoverflow.com/questions/55507497/its-possible-to-catch-ffmpeg-errors-with-python/55508096#55508096

    def _cli(self, cmd, without_output=False):
        # /usr/bin/ffmpeg  -hide_banner -nostats -i %(input_file)s -target film-dvd %(output_file)s
        # TODO probar
        errors = False
        print cmd
        print 'subprocess'
        import subprocess
        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stdoutdata, stderrdata = p.communicate()
            if p.wait() != 0:
                # Handle error / raise exception
                errors = True
                print "There were some errors"
                print '--- ERR to store----'
                print stderrdata
                print '--- OUT----'
                print stdoutdata
                print '--- STDOUT ERR----'
                print p.stdout.read()
                print '-----'
            if not errors:
                print "no errors"
            else:
                print "errors found"
            print '--- STDOUT ERR2----'
            # print p.stdout.read()
            print '--- OUT2 ----'
            print stdoutdata
            print '>> stderrdata: '
            print stderrdata  # este se almacena en el ultimo mensaje, sea exito o error
            # todo regresar campo errors para saber que estado poner en el video
            # todo regresar stderrdata, errors
            return stdoutdata, stderrdata, errors
        except OSError as e:
            print 'error'
            traceback.print_exc()
            print e
            print e.strerror
            return e.strerror, e.strerror, errors

    # def _cli(self, cmd, without_output=False):
    #     """
    #     Pass command to command line interface
    #     :param cmd: command to execute in command line interface
    #     :param without_output:
    #     :return: cli message output
    #     """
    #     if os.name == 'posix':
    #         import commands
    #         return commands.getoutput(cmd)
    #     else:
    #         import subprocess
    #         if without_output:
    #             DEVNULL = open(os.devnull, 'wb')
    #             subprocess.Popen(cmd, stdout=DEVNULL, stderr=DEVNULL)
    #         else:
    #             p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    #             return p.stdout.read()
