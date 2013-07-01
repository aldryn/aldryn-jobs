==================
Aldryn Jobs Add-On
==================

This add-on lets you:

- define translatable categories, which will appear in the menu
- add categorized, translatable job offers


Installation
============

Choose a site you want to install the add-on to from the dashboard. Then go to ``Apps -> Install app`` and click ``Install`` next to ``Jobs`` app.

Redeploy the site.

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
