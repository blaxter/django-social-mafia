from django.conf.urls.defaults import *

from social_mafia.core.views import index

urlpatterns = patterns('',
    url(r'^$', index, name="index"),
)
