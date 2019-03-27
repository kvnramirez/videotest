from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.views.generic import CreateView
from django_rq import enqueue
from video_encoding import tasks
from video_encoding.models import Format

from .models import Video




class VideoFormView(CreateView):
    model = Video
    fields = ('file',)

    success_url = '/'
    template_name = 'video_form.html'

    def get_context_data(self, *args, **kwargs):
        context = super(VideoFormView, self).get_context_data(*args, **kwargs)
        context['videos'] = Video.objects.all()
        return context


@receiver(post_save, sender=Video)
def convert_video(sender, instance, **kwargs):
    enqueue(tasks.convert_all_videos,
            instance._meta.app_label,
            instance._meta.model_name,
            instance.pk)




