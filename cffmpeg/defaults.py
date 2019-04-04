from django.conf import settings

FFMPEG_PRE_DIR = getattr(settings, 'FFMPEG_PRE_DIR', 'videos')
FFMPEG_ORIG_VIDEO = getattr(settings, 'FFMPEG_ORIG_VIDEO', 'orig')
FFMPEG_THUMB_VIDEO = getattr(settings, 'FFMPEG_THUMB_VIDEO', 'thumb')
FFMPEG_CONV_VIDEO = getattr(settings, 'FFMPEG_CONV_VIDEO', 'conv')

CONVERTER_ORIGINAL_FOLDER = getattr(settings, 'CONVERTER_ORIGINAL_FOLDER', '/o/')
CONVERTER_COVERTED_FOLDER = getattr(settings, 'CONVERTER_COVERTED_FOLDER', '/c/')
CONVERTER_THUMB_FOLDER = getattr(settings, 'CONVERTER_THUMB_FOLDER', '/t/')
