from django.conf.urls import url, include
from django.contrib import admin

from media_library.views import pending_review_list

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^django-rq/', include('django_rq.urls')),
    url(r'^pending-review/$', pending_review_list,
        name='pending-review'),
]
