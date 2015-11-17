#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class DisableMigrations(dict):

    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return "notmigrations"

gettext = lambda s: s

HELPER_SETTINGS = {
    'TIME_ZONE': 'Europe/Zurich',
    'INSTALLED_APPS': [
        'aldryn_apphooks_config',
        # needed for tests, since we need to reload server after apphook has
        # been added to a page, otherwise we cannot get a correct url.
        'aldryn_apphook_reload',
        'aldryn_categories',
        'aldryn_reversion',
        'aldryn_common',
        'bootstrap3',
        'reversion',
        'appconf',
        'filer',
        'parler',
        'sortedm2m',
        'easy_thumbnails',
        'djangocms_text_ckeditor',
        'adminsortable2',
        'standard_form',
    ],
    'THUMBNAIL_PROCESSORS': (
        'easy_thumbnails.processors.colorspace',
        'easy_thumbnails.processors.autocrop',
        'filer.thumbnail_processors.scale_and_crop_with_subject_location',
        'easy_thumbnails.processors.filters',
    ),
    'LANGUAGES': (
        ('en', 'English'),
        ('de', 'German'),
    ),
    'PARLER_LANGUAGES': {
        1: (
            {'code': 'en'},
            {'code': 'de'},
        ),
        'default': {
            'hide_untranslated': False,
        }
    },
    'CMS_LANGUAGES': {
        'default': {
            'public': True,
            'hide_untranslated': False,
            'fallbacks': ['en']

        },
        1: [
            {
                'public': True,
                'code': 'en',
                'hide_untranslated': False,
                'name': gettext('en'),
                'redirect_on_fallback': True,
            },
            {
                'public': True,
                'code': 'de',
                'hide_untranslated': False,
                'name': gettext('de'),
                'redirect_on_fallback': True,
            },
        ],
    },
    'ALDRYN_BOILERPLATE_NAME': 'legacy',
    # add aldryn_apphook_reload so that pages would be restored on apphook
    # reload.
    'MIDDLEWARE_CLASSES': [
        'aldryn_apphook_reload.middleware.ApphookReloadMiddleware',
        'django.middleware.http.ConditionalGetMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.middleware.locale.LocaleMiddleware',
        'django.middleware.common.CommonMiddleware',
        'cms.middleware.language.LanguageCookieMiddleware',
        'cms.middleware.user.CurrentUserMiddleware',
        'cms.middleware.page.CurrentPageMiddleware',
        'cms.middleware.toolbar.ToolbarMiddleware'
    ],
    # 'EMAIL_BACKEND': 'django.core.mail.backends.locmem.EmailBackend',
}


def run():
    from djangocms_helper import runner
    runner.cms('aldryn_jobs', extra_args=['--boilerplate'])

if __name__ == "__main__":
    run()
