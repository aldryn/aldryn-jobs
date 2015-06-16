==================
Aldryn Jobs Add-On
==================

.. image:: https://magnum.travis-ci.com/aldryn/aldryn-jobs.svg?token=2aLiyxMhwop2hnmajHuq&branch=master
    :target: https://magnum.travis-ci.com/aldryn/aldryn-jobs

.. image:: https://img.shields.io/coveralls/aldryn/aldryn-jobs.svg
  :target: https://coveralls.io/r/aldryn/aldryn-jobs

This add-on lets you:

- define translatable categories, which will appear in the menu
- add categorized, translatable job offers


Installation
============

Aldryn Platform Users
---------------------

Choose a site you want to install the add-on to from the dashboard. Then go to ``Apps -> Install app`` and click ``Install`` next to ``Aldryn Jobs`` app.

Redeploy the site.

Manuall Installation
--------------------

::

    pip install aldryn-events

Add below apps to ``INSTALLED_APPS``: ::

    INSTALLED_APPS = [
        …
        'absolute',
        'aldryn_common',
        'aldryn_boilerplates',
        'aldryn_apphooks_config',
        'aldryn_reversion',
        'aldryn_categories',
        'aldryn_jobs',
        'emailit',
        'parler',
        'standard_form',
        …
    ]

Add desired parler languages to settings (http://django-parler.readthedocs.org/en/latest/configuration.html),
but please be sure to use same language codes as ``CMS_LANGUAGES`` does: ::

    PARLER_LANGUAGES = {
        1: (
            {'code': 'en'},
            {'code': 'de'},
        ),
        'default': {
            'hide_untranslated': False,
        }
    }

Configure ``aldryn-boilerplates`` (https://pypi.python.org/pypi/aldryn-boilerplates/).

To use the old templates, set ``ALDRYN_BOILERPLATE_NAME='legacy'``.
To use https://github.com/aldryn/aldryn-boilerplate-standard (recommended, will be renamed to
``aldryn-boilerplate-bootstrap3``) set ``ALDRYN_BOILERPLATE_NAME='bootstrap3'``.


Adding a job offer
==================

You can define categories and job offers now in the admin panel.

In order to display them, create a CMS page (e.g ``/jobs/``) and install the app there (choose ``Jobs`` from the ``Advanced Settings -> Application`` dropdown).

Now redeploy the site again.

The above CMS site has become a job offer listing.


Attachment Storage
==================

While applying for job offer viewers can attach files. Those files are saved and stored using Django's file storage API. It is your responsibility to specify appropriate (secure) storage, in order to make the files unavailable for not authorized access.

This can be achieved by configuring the storage via below options:

ALDRYN_JOBS_ATTACHMENT_STORAGE
------------------------------

The storage object that is going to be passed directly to ``FileField`` constructor.

Please reference Django's file storage API documentation for more info.

Default: ``None`` (which means ``django.core.files.storage.default_storage`` is going to be used).

ALDRYN_JOBS_ATTACHMENT_UPLOAD_DIR
---------------------------------

The directory atachments are going to be uploaded into.

Default: ``attachments/%Y/%m/``.


File Count & Size
-----------------

* ``ALDRYN_JOBS_ATTACHMENTS_MAX_COUNT``: Max amount of files to be uploadable (default: 5)
* ``ALDRYN_JOBS_ATTACHMENTS_MIN_COUNT``: Min amount of files to be uploadable (default: 0)
* ``ALDRYN_JOBS_ATTACHMENTS_MAX_FILE_SIZE``: Max file size (each) (default: 5MB)


Sending Emails
==============

Please refer to django-emailit_ documentation for info on installation.

.. _django-emailit : http://github.com/divio/django-emailit
