class VideoEncodingError(Exception):
    pass


class FFmpegError(VideoEncodingError):
    def __init__(self, *args, **kwargs):
        self.msg = args[0]
        print 'msg: '
        print self.msg
        super(VideoEncodingError, self).__init__(*args, **kwargs)


class InvalidTimeError(VideoEncodingError):
    pass
