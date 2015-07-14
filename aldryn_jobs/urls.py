# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url

from .views import CategoryJobOpeningList, JobOpeningDetail, JobOpeningList

# default view (root url) which is pointing to ^$ url
DEFAULT_VIEW = 'job-opening-list'

urlpatterns = patterns(
    '',

    url(r'^$', JobOpeningList.as_view(),
        name='job-opening-list'),

    url(r'^(?P<category_slug>\w[-_\w]*)/$',
        CategoryJobOpeningList.as_view(),
        name='category-job-opening-list'),

    url(r'^(?P<category_slug>\w[-_\w]*)/(?P<job_opening_slug>\w[-_\w]*)/$',
        JobOpeningDetail.as_view(),
        name='job-opening-detail'),
)
