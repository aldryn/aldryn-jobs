# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from .views import CategoryJobOfferList, JobOfferDetail, JobOfferList, \
    ConfirmNewsletterSignup, ConfirmNewsletterNotFound, SuccessRegistrationMessage

urlpatterns = patterns(
    '',
    url(r'^$', JobOfferList.as_view(),
        name='job-offer-list'),

    url(r'^(?P<category_slug>\w[-_\w]*)/$',
        CategoryJobOfferList.as_view(),
        name='category-job-offer-list'),

    url(r'^(?P<category_slug>\w[-_\w]*)/(?P<job_offer_slug>\w[-_\w]*)/$',
        JobOfferDetail.as_view(),
        name='job-offer-detail'),

    url(r'^confirm_newsletter/key-not-found/$',
        ConfirmNewsletterNotFound.as_view(),
        name="confirm_newsletter_not_found"),

    url(r'^confirm_newsletter/registration-notification/$',
        SuccessRegistrationMessage.as_view(),
        name="newsletter_registration_notification"),

    url(r'^confirm_newsletter/(?P<key>\w+)/$',
        ConfirmNewsletterSignup.as_view(),
        name="confirm_newsletter_email"),


)

