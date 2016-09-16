from django.conf.urls import patterns, url

urlpatterns=patterns('',
    url("^$",'gitblog.views.gitblog_index', name='reverse_gitblog_index'),
    url("^(?P<page_num>\d+)$",'gitblog.views.gitblog_index', name='reverse_gitblog_index'),
    url(r'^entry/(?P<slug>[_\w/\+\.]+)$','gitblog.views.gitblog_entry',name='reverse_gitblog_entry'),
)
