from django.conf.urls import url, include
from django.contrib import admin

from media_library.views import pending_review_list, view_review_details

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^django-rq/', include('django_rq.urls')),
    url(r'^pending-reviews/$', pending_review_list,
        name='pending-review'),
    url(r'^view_review_details/(?P<pk>[0-9]+)/$', view_review_details, name='view_review_details'),
]
