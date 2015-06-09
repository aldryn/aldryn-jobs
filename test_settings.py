#!/usr/bin/env python
# -*- coding: utf-8 -*-
HELPER_SETTINGS = {
    'TIME_ZONE': 'Europe/Zurich',
    'INSTALLED_APPS': [
        'filer',
        'easy_thumbnails',
        'parler',
        'aldryn_common',
        'sortedm2m',
        'reversion',
        'aldryn_reversion',
        'aldryn_jobs',
        'djangocms_text_ckeditor',
    ],
    'THUMBNAIL_PROCESSORS': (
        'easy_thumbnails.processors.colorspace',
        'easy_thumbnails.processors.autocrop',
        'filer.thumbnail_processors.scale_and_crop_with_subject_location',
        'easy_thumbnails.processors.filters',
    ),
    'SOUTH_TESTS_MIGRATE': False,
    'LANGUAGES': (
        ('en', 'English'),
        ('de', 'German'),
    ),
    'ALDRYN_BOILERPLATE_NAME': 'legacy',
    'STATICFILES_FINDERS': [
        'django.contrib.staticfiles.finders.FileSystemFinder',
        # important! place right before django.contrib.staticfiles.finders.AppDirectoriesFinder
        'aldryn_boilerplates.staticfile_finders.AppDirectoriesFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    ],
    'TEMPLATE_CONTEXT_PROCESSORS': (
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
        'django.core.context_processors.i18n',
        'django.core.context_processors.debug',
        'django.core.context_processors.request',
        'django.core.context_processors.media',
        'django.core.context_processors.csrf',
        'django.core.context_processors.tz',
        'sekizai.context_processors.sekizai',
        'django.core.context_processors.static',
        'cms.context_processors.cms_settings',
        'aldryn_boilerplates.context_processors.boilerplate'
    ),
    'TEMPLATE_LOADERS': (
        'django.template.loaders.filesystem.Loader',
        # important! place right before django.template.loaders.app_directories.Loader
        'aldryn_boilerplates.template_loaders.AppDirectoriesLoader',
        'django.template.loaders.app_directories.Loader',
        'django.template.loaders.eggs.Loader'
    )
    # 'EMAIL_BACKEND': 'django.core.mail.backends.locmem.EmailBackend',
}

def run():
    from djangocms_helper import runner
    runner.cms('aldryn_jobs')

if __name__ == "__main__":
    run()
