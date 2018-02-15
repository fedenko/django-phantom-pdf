from __future__ import absolute_import
from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

from tests.test_app.views import IndexView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^admin/', include(admin.site.urls)),
]
