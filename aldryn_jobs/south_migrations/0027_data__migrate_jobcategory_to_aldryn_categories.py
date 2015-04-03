# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from aldryn_categories.models import Category as NoFrozenCategory


class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Don't use "from appname.models import ModelName".
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.
        Category = orm['aldryn_categories.Category']
        JobCategory = orm.JobCategory
        JobCategoryOpts = orm.JobCategoryOpts
        for old_category in JobCategory.objects.all():
            # This is maybe wrong but using the model out of 'orm' (not frozen)
            # we can access add_root. Copy all the treebeard category creation
            # into migration is a big overhead, but would be the perfect thing
            # to do.
            en_tr = old_category.translations.get(language_code='en')
            new_category = NoFrozenCategory.add_root(
                name=en_tr.name,
                slug=en_tr.slug,
            )
            new_category = Category.objects.get(pk=new_category.pk)

            # When creating default translation parler use as default 'en-us',
            # so we fix it here because we use only 'en'.
            en_tr = new_category.translations.get()
            en_tr.language_code = 'en'
            en_tr.save()

            # add other translations, we can't use create_translations
            # in migrations.
            for tr in old_category.translations.exclude(language_code='en'):
                new_category.translations.create(
                    language_code=tr.language_code,
                    name=tr.name,
                    slug=tr.slug,
                )

            for job in old_category.jobs.all():
                job.category_new = new_category
                job.category = None
                job.save()

            job_opts = JobCategoryOpts.objects.create(
                category_id=new_category.pk,
                app_config=old_category.app_config,
                # ordering isn't migrated since aldryn-categories provide a way
                # to order categories already
            )
            job_opts.supervisors = old_category.supervisors.all()
            job_opts.save()

            old_category.delete()

    def backwards(self, orm):
        "Write your backwards methods here."
        Category = orm['aldryn_categories.Category']
        JobCategory = orm.JobCategory

        for new_category in Category.objects.all():
            # create the old category
            old_category = JobCategory.objects.create(
                app_config=new_category.jobs_opts.app_config
            )
            old_category.supervisors = new_category.jobs_opts.supervisors.all()

            # create default translation
            en_tr = new_category.translations.get(language_code='en')
            old_category.translations.create(
                language_code='en',
                name=en_tr.name,
                slug=en_tr.slug
            )
            for tr in new_category.translations.exclude(language_code='en'):
                # create another translations
                old_category.translations.create(
                    language_code=tr.language_code,
                    name=tr.name,
                    slug=tr.slug,
                )

            for job in new_category.job_offers.all():
                job.category = old_category
                job.category_new = None
                job.save()

            old_category.save()
            new_category.delete()

    models = {
        u'aldryn_categories.category': {
            'Meta': {'object_name': 'Category'},
            'depth': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'rgt': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'aldryn_categories.categorytranslation': {
            'Meta': {'unique_together': "[(u'language_code', u'slug'), (u'language_code', u'master')]", 'object_name': 'CategoryTranslation', 'db_table': "u'aldryn_categories_category_translation'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            u'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': u"orm['aldryn_categories.Category']"}),
            'name': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'default': "u''", 'max_length': '255', 'blank': 'True'})
        },
        u'aldryn_jobs.jobapplication': {
            'Meta': {'ordering': "['-created']", 'object_name': 'JobApplication'},
            'app_config': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['aldryn_jobs.JobsConfig']", 'null': 'True'}),
            'cover_letter': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_rejected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'job_offer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['aldryn_jobs.JobOffer']"}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'rejection_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'salutation': ('django.db.models.fields.CharField', [], {'default': "'male'", 'max_length': '20', 'blank': 'True'})
        },
        u'aldryn_jobs.jobapplicationattachment': {
            'Meta': {'object_name': 'JobApplicationAttachment'},
            'application': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': u"orm['aldryn_jobs.JobApplication']"}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'aldryn_jobs.jobcategoriesplugin': {
            'Meta': {'object_name': 'JobCategoriesPlugin'},
            'app_config': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['aldryn_jobs.JobsConfig']", 'null': 'True'}),
            u'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'aldryn_jobs.jobcategory': {
            'Meta': {'ordering': "['ordering']", 'object_name': 'JobCategory'},
            'app_config': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['aldryn_jobs.JobsConfig']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'supervisors': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'job_offer_categories'", 'blank': 'True', 'to': u"orm['auth.User']"})
        },
        u'aldryn_jobs.jobcategoryopts': {
            'Meta': {'object_name': 'JobCategoryOpts'},
            'app_config': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['aldryn_jobs.JobsConfig']", 'null': 'True'}),
            'category': ('aldryn_categories.fields.CategoryOneToOneField', [], {'related_name': "'jobs_opts'", 'unique': 'True', 'to': u"orm['aldryn_categories.Category']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'supervisors': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'job_categories_opts'", 'blank': 'True', 'to': u"orm['auth.User']"})
        },
        u'aldryn_jobs.jobcategorytranslation': {
            'Meta': {'unique_together': "[['slug', 'language_code'], (u'language_code', u'master')]", 'object_name': 'JobCategoryTranslation', 'db_table': "u'aldryn_jobs_jobcategory_translation'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            u'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': u"orm['aldryn_jobs.JobCategory']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'aldryn_jobs.joblistplugin': {
            'Meta': {'object_name': 'JobListPlugin'},
            'app_config': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['aldryn_jobs.JobsConfig']", 'null': 'True'}),
            u'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'joboffers': ('sortedm2m.fields.SortedManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['aldryn_jobs.JobOffer']", 'null': 'True', 'blank': 'True'})
        },
        u'aldryn_jobs.jobnewsletterregistrationplugin': {
            'Meta': {'object_name': 'JobNewsletterRegistrationPlugin', '_ormbases': ['cms.CMSPlugin']},
            u'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'mail_to_group': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False'})
        },
        u'aldryn_jobs.joboffer': {
            'Meta': {'ordering': "['category__ordering', 'category', '-created']", 'object_name': 'JobOffer'},
            'app_config': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['aldryn_jobs.JobsConfig']", 'null': 'True'}),
            'can_apply': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'jobs'", 'null': 'True', 'to': u"orm['aldryn_jobs.JobCategory']"}),
            'category_new': ('aldryn_categories.fields.CategoryForeignKey', [], {'default': 'None', 'related_name': "'job_offers'", 'null': 'True', 'to': u"orm['aldryn_categories.Category']"}),
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'publication_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'publication_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'aldryn_jobs.joboffertranslation': {
            'Meta': {'unique_together': "[['slug', 'language_code'], (u'language_code', u'master')]", 'object_name': 'JobOfferTranslation', 'db_table': "u'aldryn_jobs_joboffer_translation'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'lead_in': ('djangocms_text_ckeditor.fields.HTMLField', [], {'blank': 'True'}),
            u'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': u"orm['aldryn_jobs.JobOffer']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'aldryn_jobs.jobsconfig': {
            'Meta': {'unique_together': "(('type', 'namespace'),)", 'object_name': 'JobsConfig'},
            'app_data': ('app_data.fields.AppDataField', [], {'default': "'{}'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'namespace': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '100'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'aldryn_jobs.newslettersignup': {
            'Meta': {'object_name': 'NewsletterSignup'},
            'confirmation_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'default_language': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '32', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_disabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'recipient': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'signup_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'aldryn_jobs.newslettersignupuser': {
            'Meta': {'object_name': 'NewsletterSignupUser'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'signup': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'related_user'", 'to': u"orm['aldryn_jobs.NewsletterSignup']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'newsletter_signup'", 'to': u"orm['auth.User']"})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'changed_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.CMSPlugin']", 'null': 'True', 'blank': 'True'}),
            'placeholder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['aldryn_categories', 'aldryn_jobs']
    symmetrical = True
