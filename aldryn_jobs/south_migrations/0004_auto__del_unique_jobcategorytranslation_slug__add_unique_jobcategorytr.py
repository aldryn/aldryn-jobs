# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'JobCategoryTranslation', fields ['slug', 'language_code']
        db.create_unique('aldryn_jobs_jobcategory_translation', ['slug', 'language_code'])

        # Adding unique constraint on 'JobOfferTranslation', fields ['slug', 'language_code']
        db.create_unique('aldryn_jobs_joboffer_translation', ['slug', 'language_code'])

    def backwards(self, orm):
        # Removing unique constraint on 'JobOfferTranslation', fields ['slug', 'language_code']
        db.delete_unique('aldryn_jobs_joboffer_translation', ['slug', 'language_code'])

        # Removing unique constraint on 'JobCategoryTranslation', fields ['slug', 'language_code']
        db.delete_unique('aldryn_jobs_jobcategory_translation', ['slug', 'language_code'])

    models = {
        'aldryn_jobs.jobcategory': {
            'Meta': {'ordering': "['ordering']", 'object_name': 'JobCategory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'aldryn_jobs.jobcategorytranslation': {
            'Meta': {'unique_together': "[['slug', 'language_code'], ('language_code', 'master')]", 'object_name': 'JobCategoryTranslation', 'db_table': "'aldryn_jobs_jobcategory_translation'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': "orm['aldryn_jobs.JobCategory']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'blank': 'True'})
        },
        'aldryn_jobs.joboffer': {
            'Meta': {'ordering': "['category__ordering', 'category', '-created']", 'object_name': 'JobOffer'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'jobs'", 'to': "orm['aldryn_jobs.JobCategory']"}),
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'publication_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'publication_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'aldryn_jobs.joboffertranslation': {
            'Meta': {'unique_together': "[['slug', 'language_code'], ('language_code', 'master')]", 'object_name': 'JobOfferTranslation', 'db_table': "'aldryn_jobs_joboffer_translation'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': "orm['aldryn_jobs.JobOffer']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'blank': 'True'}),
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
