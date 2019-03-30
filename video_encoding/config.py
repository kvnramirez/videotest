from appconf import AppConf
from django.conf import settings  # NOQA


class VideoEncodingAppConf(AppConf):
    THREADS = 1
    PROGRESS_UPDATE = 30
    BACKEND = 'video_encoding.backends.ffmpeg.FFmpegBackend'
    BACKEND_PARAMS = {}
    FORMATS = {
        'FFmpeg': [
            {
                'name': 'mp4_sd',
                'extension': 'mp4',
                'params': [
                    '-codec:v', 'libx264', '-crf', '20', '-preset', 'medium',
                    '-b:v', '1500k', '-maxrate', '1500k', '-bufsize', '2000k',
                    '-vf', 'scale=-2:480',  # http://superuser.com/a/776254
                    '-codec:a', 'aac', '-b:a', '128k', '-strict', '-2',
                ],
            },
            {
                'name': 'mov_sd',
                'extension': 'mov',
                'params': [
                    '-codec:v', 'libx264', '-crf', '20', '-preset', 'medium',
                    '-b:v', '1500k', '-maxrate', '1500k', '-bufsize', '2000k',
                    '-vf', 'scale=-2:480',
                    '-codec:a', 'aac', '-b:a', '128k', '-strict', '-2',
                ],
            },
        ]
    }
