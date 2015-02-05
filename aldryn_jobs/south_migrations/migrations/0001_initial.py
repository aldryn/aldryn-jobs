# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'JobCategoryTranslation'
        db.create_table('aldryn_jobs_jobcategory_translation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', null=True, to=orm['aldryn_jobs.JobCategory'])),
        ))
        db.send_create_signal('aldryn_jobs', ['JobCategoryTranslation'])

        # Adding unique constraint on 'JobCategoryTranslation', fields ['language_code', 'master']
        db.create_unique('aldryn_jobs_jobcategory_translation', ['language_code', 'master_id'])

        # Adding model 'JobCategory'
        db.create_table('aldryn_jobs_jobcategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ordering', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('aldryn_jobs', ['JobCategory'])

        # Adding model 'JobOfferTranslation'
        db.create_table('aldryn_jobs_joboffer_translation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', null=True, to=orm['aldryn_jobs.JobOffer'])),
        ))
        db.send_create_signal('aldryn_jobs', ['JobOfferTranslation'])

        # Adding unique constraint on 'JobOfferTranslation', fields ['language_code', 'master']
        db.create_unique('aldryn_jobs_joboffer_translation', ['language_code', 'master_id'])

        # Adding model 'JobOffer'
        db.create_table('aldryn_jobs_joboffer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cms.Placeholder'], null=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(related_name='jobs', to=orm['aldryn_jobs.JobCategory'])),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('aldryn_jobs', ['JobOffer'])


    def backwards(self, orm):
        # Removing unique constraint on 'JobOfferTranslation', fields ['language_code', 'master']
        db.delete_unique('aldryn_jobs_joboffer_translation', ['language_code', 'master_id'])

        # Removing unique constraint on 'JobCategoryTranslation', fields ['language_code', 'master']
        db.delete_unique('aldryn_jobs_jobcategory_translation', ['language_code', 'master_id'])

        # Deleting model 'JobCategoryTranslation'
        db.delete_table('aldryn_jobs_jobcategory_translation')

        # Deleting model 'JobCategory'
        db.delete_table('aldryn_jobs_jobcategory')

        # Deleting model 'JobOfferTranslation'
        db.delete_table('aldryn_jobs_joboffer_translation')

        # Deleting model 'JobOffer'
        db.delete_table('aldryn_jobs_joboffer')


    models = {
        'aldryn_jobs.jobcategory': {
            'Meta': {'ordering': "['ordering']", 'object_name': 'JobCategory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {})
        },
        'aldryn_jobs.jobcategorytranslation': {
            'Meta': {'unique_together': "[('language_code', 'master')]", 'object_name': 'JobCategoryTranslation', 'db_table': "'aldryn_jobs_jobcategory_translation'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': "orm['aldryn_jobs.JobCategory']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'})
        },
        'aldryn_jobs.joboffer': {
            'Meta': {'ordering': "['-created']", 'object_name': 'JobOffer'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'jobs'", 'to': "orm['aldryn_jobs.JobCategory']"}),
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'aldryn_jobs.joboffertranslation': {
            'Meta': {'unique_together': "[('language_code', 'master')]", 'object_name': 'JobOfferTranslation', 'db_table': "'aldryn_jobs_joboffer_translation'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': "orm['aldryn_jobs.JobOffer']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        }
    }

    complete_apps = ['aldryn_jobs']