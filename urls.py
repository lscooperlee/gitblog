from django.conf.urls import patterns, url

urlpatterns=patterns('',
    url("^$",'gitblog.views.gitblog_index', name='reverse_cblog_index'),
)
