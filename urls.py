from django.conf.urls import url, include
from django.contrib import admin

from media_library.views import VideoFormView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', VideoFormView.as_view()),
    url(r'^django-rq/', include('django_rq.urls')),
]
