# -*- coding: utf-8 -*-

import datetime
import logging
import os
import re

from django_ffmpeg.models import ConvertVideo, EnqueuedVideo
from pytz import timezone

logger = logging.getLogger(__name__)


def convert_instance(format, video):
    vid_ext = format['extension']
    vid_command = format['command']
    vid_thumb_command = format['thumb_command']
    if not video:
        logger.info('No video found. Bypassing call...')
        return

    # # Choosing one unconverted video
    # try:
    #     video = ConvertVideo.objects.filter(convert_status='pending')[0]
    # except IndexError:
    #     logger.info('No video found. Bypassing call...')
    #     return

    if vid_ext == "mov":
        video.convert_status_mov = 'started'
    else:
        video.convert_status = 'started'
    # video.convert_status = 'started'
    video.save()

    # Choosing converting command
    filepath = video.video.path
    full_name = filepath.split('/')[-1]

    video_info = {
        'name': full_name,
        'extension': full_name.split('.')[-1],
    }

    # cmds = ConvertingCommand.objects.filter(is_enabled=True)
    # cmd = None
    # for c in cmds:
    #     data = video_info.get(c.match_by)
    #     if not data:
    #         continue
    #     if re.match(c.match_regex, data):
    #         cmd = c
    #         break

    if not vid_command:
        logger.error('Conversion command not found...')
        # video.convert_status = 'error'
        if vid_ext == "mov":
            video.convert_status_mov = 'error'
            video.last_convert_msg_mov = 'Conversion command not found'
        else:
            video.convert_status = 'error'
            video.last_convert_msg = 'Conversion command not found'
        # video.last_convert_msg = 'Conversion command not found'
        video.save()
        return

    # Convert video
    if vid_ext == "mov":
        video.convert_extension_2 = vid_ext
    else:
        video.convert_extension = vid_ext
    try:
        c = vid_command % {
            'input_file': filepath,
            'output_file': video.converted_path,
        }
        logger.info('Converting video command: %s' % c)
        output = _cli(c)
        logger.info('Converting video result: %s' % output)
    except Exception as e:
        logger.error('Converting video error', exc_info=True)
        if vid_ext == "mov":
            video.convert_status_mov = 'error'
            video.last_convert_msg_mov = u'Exception while converting'
        else:
            video.convert_status = 'error'
            video.last_convert_msg = u'Exception while converting'
        # video.convert_status = 'error'
        # video.last_convert_msg = u'Exception while converting'
        video.save()
        raise

    # Convert thumb
    try:
        if not video.thumb:
            cmd = vid_thumb_command % {
                'in_file': filepath,
                'out_file': video.thumb_video_path,
                'thumb_frame': video.thumb_frame,
            }
            _cli(cmd, True)
            logger.info('Creating thumbnail command: %s' % cmd)
    except:
        logger.error('Converting thumb error', exc_info=True)

    if vid_ext == "mov":
        video.convert_status_mov = 'converted'
        video.last_convert_msg_mov = repr(output).replace('\\n', '\n').strip('\'')
        video.converted_mov_at = datetime.datetime.now(tz=timezone('UTC'))
        video.output_video_mov.name = video.converted_path_mov
    else:
        video.convert_status = 'converted'
        video.last_convert_msg = repr(output).replace('\\n', '\n').strip('\'')
        video.converted_at = datetime.datetime.now(tz=timezone('UTC'))
        video.output_video_mp4.name = video.converted_path_mp4
    # video.convert_status = 'converted'
    # video.last_convert_msg = repr(output).replace('\\n', '\n').strip('\'')
    # if vid_ext == "mov":
    #     video.converted_mov_at = datetime.datetime.now(tz=timezone('UTC'))
    # else:
    #     video.converted_at = datetime.datetime.now(tz=timezone('UTC'))
    # video.converted_at = datetime.datetime.now(tz=timezone('UTC'))
    video.save()


def convert_video(convert_video_id, enqueue_video_id):

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

    video_info = {
        'name': full_name,
        'extension': full_name.split('.')[-1],
    }

    if not video_command:
        logger.error('Conversion command not found...')
        enqueue_video.convert_status = 'error'
        enqueue_video.last_convert_msg = 'Conversion command not found'
        enqueue_video.save()
        return

    try:
        c = video_command % {
            'input_file': filepath,
            'output_file': converted_path(video_extension, convert_video_object),
        }
        logger.info('Converting video command: %s' % c)
        output = _cli(c)
        logger.info('Converting video result: %s' % output)
    except Exception as e:
        logger.error('Converting video error', exc_info=True)
        enqueue_video.convert_status = 'error'
        enqueue_video.last_convert_msg = u'Exception while converting'
        enqueue_video.save()
        raise

    # Convert thumb
    try:
        if not enqueue_video.thumb:
            cmd = video_thumb_command % {
                'in_file': filepath,
                'out_file': thumb_video_path(convert_video_object),
                'thumb_frame': enqueue_video.thumb_frame,
            }
            _cli(cmd, True)
            logger.info('Creating thumbnail command: %s' % cmd)
    except:
        logger.error('Converting thumb error', exc_info=True)

    enqueue_video.convert_status = 'converted'
    enqueue_video.last_convert_msg = repr(output).replace('\\n', '\n').strip('\'')
    enqueue_video.converted_at = datetime.datetime.now(tz=timezone('UTC'))
    enqueue_video.converted_video.name = converted_path(video_extension, convert_video_object)
    enqueue_video.save()


def converted_path(convert_extension, original_video):
    """
    Generate new path for converted video
    :param convert_extension: extension of output file
    :param original_video: original video object to extract filepath
    :return: new path to use
    """
    if not convert_extension:
        return None
    filepath = original_video.video.path
    filepath.replace('_original', '_x264')
    print re.sub(r'[^\.]{1,10}$', convert_extension, filepath)
    return re.sub(r'[^\.]{1,10}$', convert_extension, filepath)


def thumb_video_path(original_video):
        """
        Generate new path for video thumbnail
        :param original_video: original video object to extract filepath
        :return: new path to use
        """
        filepath = original_video.video.path
        filepath.replace('_original', '_thumb')
        return re.sub(r'[^\.]{1,10}$', 'jpg', filepath)


def _cli(cmd, without_output=False):
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
