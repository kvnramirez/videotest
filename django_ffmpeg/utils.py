# -*- coding: utf-8 -*-

import datetime
import logging
import os
import re
import traceback

from django_ffmpeg.models import Video, ConvertingCommand
from pytz import timezone

logger = logging.getLogger(__name__)


class Converter(object):

    def convert(self):
        print 'convert'
        # Choosing one unconverted video
        try:
            video = Video.objects.filter(convert_status='pending')[0]
        except IndexError:
            logger.info('No video found. Bypassing call...')
            return
        video.convert_status = 'started'
        video.save()

        # Choosing converting command
        filepath = video.video.path
        full_name = filepath.split('/')[-1]

        video_info = {
            'name': full_name,
            'extension': full_name.split('.')[-1],
        }
        cmds = ConvertingCommand.objects.filter(is_enabled=True)
        cmd = None
        for c in cmds:
            data = video_info.get(c.match_by)
            if not data:
                continue
            if re.match(c.match_regex, data):
                cmd = c
                break

        if not cmd:
            logger.error('Conversion command not found...')
            video.convert_status = 'error'
            video.last_convert_msg = 'Conversion command not found'
            video.save()
            return

        # Convert video
        video.convert_extension = cmd.convert_extension
        try:
            c = cmd.command % {
                'input_file': filepath,
                'output_file': video.converted_path,
            }
            logger.info('Converting video command: %s' % c)
            output = self._cli(c)
            print 'output: '
            print output
            logger.info('Converting video result: %s' % output)
        except Exception as e:
            logger.error('Converting video error', exc_info=True)
            video.convert_status = 'error'
            video.last_convert_msg = u'Exception while converting'
            video.save()
            raise

        # Convert thumb
        try:
            if not video.thumb:
                cmd = cmd.thumb_command % {
                    'in_file': filepath,
                    'out_file': video.thumb_video_path,
                    'thumb_frame': video.thumb_frame,
                }
                self._cli(cmd, True)
                logger.info('Creating thumbnail command: %s' % cmd)
        except:
            logger.error('Converting thumb error', exc_info=True)

        print 'holi'

        video.convert_status = 'converted'
        video.last_convert_msg = repr(output).replace('\\n', '\n').strip('\'')
        video.converted_at = datetime.datetime.now(tz=timezone('UTC'))
        video.save()

    # def _cli(self, cmd, without_output=False):
    #     print 'cli'
    #     if os.name == 'posix':
    #         print 'posix'
    #         import commands
    #         return commands.getoutput(cmd)
    #     else:
    #         print 'subprocess'
    #         import subprocess
    #         if without_output:
    #             print 'without_output'
    #             DEVNULL = open(os.devnull, 'wb')
    #             subprocess.Popen(cmd, stdout=DEVNULL, stderr=DEVNULL)
    #         else:
    #             print 'else'
    #             p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    #             print 'stderr'
    #             print p.stderr
    #             return p.stdout.read()

    def _cli(self, cmd, without_output=False):
        # /usr/bin/ffmpeg  -hide_banner -nostats -i %(input_file)s -target film-dvd %(output_file)s
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
            print "holi"
            print '--- OUT2 ----'
            print stdoutdata
            print '>> stderrdata: '
            print stderrdata # este se almacena en el ultimo mensaje, sea exito o error
            # todo regresar campo errors para saber que estado poner en el video
            # todo regresar stderrdata, errors
            return stdoutdata
        except OSError as e:
            print 'error'
            traceback.print_exc()
            print e
            print e.strerror
