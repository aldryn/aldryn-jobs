#########
Reference
#########


******************
Attachment storage
******************

While applying for vacancies, visitors can attach files. Those files are saved and stored using Django's file storage API. You need to ensure that the storage options you choose are appropriately secured against unauthorised access:

ALDRYN_JOBS_ATTACHMENT_STORAGE
==============================

The storage object that is going to be passed directly to ``FileField`` constructor.

Refer to Django's file storage API documentation for more info.

Default: ``None`` (which means ``django.core.files.storage.default_storage`` is going to be used).

ALDRYN_JOBS_ATTACHMENT_UPLOAD_DIR
=================================

The directory atachments are going to be uploaded into.

Default: ``attachments/%Y/%m/``.


File Count & Size
=================

* ``ALDRYN_JOBS_ATTACHMENTS_MAX_COUNT``: Max amount of files to be uploadable (default: 5)
* ``ALDRYN_JOBS_ATTACHMENTS_MIN_COUNT``: Min amount of files to be uploadable (default: 0)
* ``ALDRYN_JOBS_ATTACHMENTS_MAX_FILE_SIZE``: Max file size (each) (default: 5MB)


Sending email
=============

Please refer to django-emailit_ documentation for info on installation.

.. _django-emailit : http://github.com/divio/django-emailit

