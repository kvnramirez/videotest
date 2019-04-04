# -*- coding: utf-8 -*-
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from django.urls import reverse

from cffmpeg.models import ConvertVideo
from media_library.forms import ReviewForm


# class VideoFormView(CreateView):
#     model = Video
#     fields = ('file',)
#
#     success_url = '/video'
#     template_name = 'video_form.html'
#
#     def get_context_data(self, *args, **kwargs):
#         context = super(VideoFormView, self).get_context_data(*args, **kwargs)
#         context['videos'] = Video.objects.all()
#         return context


def pending_review_list(request):
    """ Pending videos review list """
    paginate_by = 20
    denuncias = ConvertVideo.objects.all().order_by(
        '-created_at')  # videos convertidos/erroneos pendientes de revision

    paginator = Paginator(denuncias, paginate_by)

    page = request.GET.get('page')

    try:
        file = paginator.page(page)
    except PageNotAnInteger:
        file = paginator.page(1)
    except EmptyPage:
        file = paginator.page(paginator.num_pages)

    return render(request, 'pending_reviews.html', {'reviews': file})


def view_review_details(request, pk):
    """ Review details """
    try:
        review = ConvertVideo.objects.get(id=pk)
    except:
        re_url = reverse('pending_review_list')
        return redirect('%s?status=4' % re_url)

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect('view_review_details', pk=review.pk)
    else:
        form = ReviewForm(instance=review)

    return render(request, 'view_review_details.html', {'form': form})
