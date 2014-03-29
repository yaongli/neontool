#!/usr/bin/env python
# coding: utf-8
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from cvs_history.views import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    #url(r'^$', 'cvs_history.views.home', name='home'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns = patterns('',
    url(r'^cvs/$', CvsHistoryList.as_view()),
    url(r'^cvs/p/(\d+)/?$', CvsHistoryList.as_view()),
    url(r'^cvs/(\w+)/?$', CvsHistoryAuthorList.as_view()),
    url(r'^jira10/?$', LastTenJiraView.as_view()),
    url(r'^jira10/p/(\d+)/?$', LastTenJiraView.as_view()),
    url(r'^jira/?$', JiraList.as_view()),
    url(r'^jira/p/(\d+)/?$', JiraList.as_view()),
    url(r'^jira/([\w-]+)/?$', JiraView.as_view()),
    url(r'^$', LastTenJiraView.as_view()),
)
