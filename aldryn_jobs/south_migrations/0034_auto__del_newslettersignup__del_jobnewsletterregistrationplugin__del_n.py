# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'JobCategoryTranslation', fields ['slug', 'language_code']
        db.delete_unique(u'aldryn_jobs_jobcategory_translation', ['slug', 'language_code'])

        # Removing unique constraint on 'JobOpeningTranslation', fields ['slug', 'language_code']
        db.delete_unique(u'aldryn_jobs_jobopening_translation', ['slug', 'language_code'])

        # Deleting model 'NewsletterSignup'
        db.delete_table(u'aldryn_jobs_newslettersignup')

        # Deleting model 'JobNewsletterRegistrationPlugin'
        db.delete_table(u'aldryn_jobs_jobnewsletterregistrationplugin')

        # Removing M2M table for field mail_to_group on 'JobNewsletterRegistrationPlugin'
        db.delete_table(db.shorten_name(u'aldryn_jobs_jobnewsletterregistrationplugin_mail_to_group'))

        # Deleting model 'NewsletterSignupUser'
        db.delete_table(u'aldryn_jobs_newslettersignupuser')

        # Deleting field 'JobsConfig.placeholder_jobs_newsletter_registration'
        db.delete_column(u'aldryn_jobs_jobsconfig', 'placeholder_jobs_newsletter_registration_id')


    def backwards(self, orm):
        # Adding model 'NewsletterSignup'
        db.create_table(u'aldryn_jobs_newslettersignup', (
            ('recipient', self.gf('django.db.models.fields.EmailField')(max_length=75, unique=True)),
            ('app_config', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['aldryn_jobs.JobsConfig'], null=True)),
            ('is_verified', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_disabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('default_language', self.gf('django.db.models.fields.CharField')(default=u'', max_length=32, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('signup_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('confirmation_key', self.gf('django.db.models.fields.CharField')(max_length=40, unique=True)),
        ))
        db.send_create_signal(u'aldryn_jobs', ['NewsletterSignup'])

        # Adding model 'JobNewsletterRegistrationPlugin'
        db.create_table(u'aldryn_jobs_jobnewsletterregistrationplugin', (
            (u'cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cms.CMSPlugin'], unique=True, primary_key=True)),
            ('app_config', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['aldryn_jobs.JobsConfig'], null=True)),
        ))
        db.send_create_signal(u'aldryn_jobs', ['JobNewsletterRegistrationPlugin'])

        # Adding M2M table for field mail_to_group on 'JobNewsletterRegistrationPlugin'
        m2m_table_name = db.shorten_name(u'aldryn_jobs_jobnewsletterregistrationplugin_mail_to_group')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('jobnewsletterregistrationplugin', models.ForeignKey(orm[u'aldryn_jobs.jobnewsletterregistrationplugin'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['jobnewsletterregistrationplugin_id', 'group_id'])

        # Adding model 'NewsletterSignupUser'
        db.create_table(u'aldryn_jobs_newslettersignupuser', (
            ('signup', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'related_user', to=orm['aldryn_jobs.NewsletterSignup'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'newsletter_signup', to=orm['auth.User'])),
        ))
        db.send_create_signal(u'aldryn_jobs', ['NewsletterSignupUser'])

        # Adding unique constraint on 'JobOpeningTranslation', fields ['slug', 'language_code']
        db.create_unique(u'aldryn_jobs_jobopening_translation', ['slug', 'language_code'])

        # Adding unique constraint on 'JobCategoryTranslation', fields ['slug', 'language_code']
        db.create_unique(u'aldryn_jobs_jobcategory_translation', ['slug', 'language_code'])

        # Adding field 'JobsConfig.placeholder_jobs_newsletter_registration'
        db.add_column(u'aldryn_jobs_jobsconfig', 'placeholder_jobs_newsletter_registration',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'aldryn_jobs_newsletter_registration', null=True, to=orm['cms.Placeholder']),
                      keep_default=False)


    models = {
        u'aldryn_jobs.jobapplication': {
            'Meta': {'ordering': "[u'-created']", 'object_name': 'JobApplication'},
            'cover_letter': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_rejected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'job_opening': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'applications'", 'to': u"orm['aldryn_jobs.JobOpening']"}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'rejection_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'salutation': ('django.db.models.fields.CharField', [], {'default': "u'male'", 'max_length': '20', 'blank': 'True'})
        },
        u'aldryn_jobs.jobapplicationattachment': {
            'Meta': {'object_name': 'JobApplicationAttachment'},
            'application': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'attachments'", 'to': u"orm['aldryn_jobs.JobApplication']"}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'aldryn_jobs.jobcategoriesplugin': {
            'Meta': {'object_name': 'JobCategoriesPlugin'},
            'app_config': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['aldryn_jobs.JobsConfig']", 'null': 'True'}),
            u'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'aldryn_jobs.jobcategory': {
            'Meta': {'ordering': "[u'ordering']", 'object_name': 'JobCategory'},
            'app_config': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'categories'", 'null': 'True', 'to': u"orm['aldryn_jobs.JobsConfig']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'supervisors': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'job_opening_categories'", 'blank': 'True', 'to': u"orm['auth.User']"})
        },
        u'aldryn_jobs.jobcategorytranslation': {
            'Meta': {'unique_together': "[(u'language_code', u'master')]", 'object_name': 'JobCategoryTranslation', 'db_table': "u'aldryn_jobs_jobcategory_translation'"},
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
            'jobopenings': ('sortedm2m.fields.SortedManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['aldryn_jobs.JobOpening']", 'null': 'True', 'blank': 'True'})
        },
        u'aldryn_jobs.jobopening': {
            'Meta': {'ordering': "[u'category__ordering', u'category', u'-created']", 'object_name': 'JobOpening'},
            'can_apply': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'jobs'", 'to': u"orm['aldryn_jobs.JobCategory']"}),
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'publication_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'publication_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'aldryn_jobs.jobopeningtranslation': {
            'Meta': {'unique_together': "[(u'language_code', u'master')]", 'object_name': 'JobOpeningTranslation', 'db_table': "u'aldryn_jobs_jobopening_translation'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'lead_in': ('djangocms_text_ckeditor.fields.HTMLField', [], {'blank': 'True'}),
            u'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': u"orm['aldryn_jobs.JobOpening']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'aldryn_jobs.jobsconfig': {
            'Meta': {'unique_together': "(('type', 'namespace'),)", 'object_name': 'JobsConfig'},
            'app_data': ('app_data.fields.AppDataField', [], {'default': "'{}'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'namespace': ('django.db.models.fields.CharField', [], {'default': 'None', 'unique': 'True', 'max_length': '100'}),
            'placeholder_jobs_detail_bottom': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'aldryn_jobs_detail_bottom'", 'null': 'True', 'to': "orm['cms.Placeholder']"}),
            'placeholder_jobs_detail_footer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'aldryn_jobs_detail_footer'", 'null': 'True', 'to': "orm['cms.Placeholder']"}),
            'placeholder_jobs_detail_top': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'aldryn_jobs_detail_top'", 'null': 'True', 'to': "orm['cms.Placeholder']"}),
            'placeholder_jobs_list_bottom': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'aldryn_jobs_list_bottom'", 'null': 'True', 'to': "orm['cms.Placeholder']"}),
            'placeholder_jobs_list_top': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'aldryn_jobs_list_top'", 'null': 'True', 'to': "orm['cms.Placeholder']"}),
            'placeholder_jobs_sidebar': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'aldryn_jobs_sidebar'", 'null': 'True', 'to': "orm['cms.Placeholder']"}),
            'placeholder_jobs_top': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'aldryn_jobs_top'", 'null': 'True', 'to': "orm['cms.Placeholder']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
            'depth': ('django.db.models.fields.PositiveIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'numchild': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.CMSPlugin']", 'null': 'True', 'blank': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'placeholder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'})
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

    complete_apps = ['aldryn_jobs']