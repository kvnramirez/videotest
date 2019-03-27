# -*- coding: utf-8 -*-
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.shortcuts import render
from django.views.generic import CreateView
from django_rq import enqueue
from video_encoding import tasks
from video_encoding.models import Format

from .models import Video, Video_revision


class VideoFormView(CreateView):
    model = Video
    fields = ('file',)

    success_url = '/'
    template_name = 'video_form.html'

    def get_context_data(self, *args, **kwargs):
        context = super(VideoFormView, self).get_context_data(*args, **kwargs)
        context['videos'] = Video.objects.all()
        return context



def pending_review_list(request):
    """ Pending videos review list """
    paginate_by = 20
    denuncias = Video_revision.objects.filter(revision=1).order_by('-create_date')  # asesorias pendientes

    paginator = Paginator(denuncias, paginate_by)

    page = request.GET.get('page')

    try:
        file = paginator.page(page)
    except PageNotAnInteger:
        file = paginator.page(1)
    except EmptyPage:
        file = paginator.page(paginator.num_pages)

    return render(request, 'pending_reviews.html', {'reviews': file})


@receiver(post_save, sender=Video)
def convert_video(sender, instance, **kwargs):
    enqueue(tasks.convert_all_videos,
            instance._meta.app_label,
            instance._meta.model_name,
            instance.pk)




