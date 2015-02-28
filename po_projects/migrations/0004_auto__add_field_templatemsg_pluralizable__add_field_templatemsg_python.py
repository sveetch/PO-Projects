# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'TemplateMsg.pluralizable'
        db.add_column(u'po_projects_templatemsg', 'pluralizable',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'TemplateMsg.python_format'
        db.add_column(u'po_projects_templatemsg', 'python_format',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'TemplateMsg.pluralizable'
        db.delete_column(u'po_projects_templatemsg', 'pluralizable')

        # Deleting field 'TemplateMsg.python_format'
        db.delete_column(u'po_projects_templatemsg', 'python_format')


    models = {
        u'po_projects.catalog': {
            'Meta': {'object_name': 'Catalog'},
            'header_comment': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locale': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'mime_headers': ('django.db.models.fields.TextField', [], {}),
            'project_version': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['po_projects.ProjectVersion']"})
        },
        u'po_projects.project': {
            'Meta': {'object_name': 'Project'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'domain': ('django.db.models.fields.CharField', [], {'default': "'django'", 'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '75'})
        },
        u'po_projects.projectversion': {
            'Meta': {'object_name': 'ProjectVersion'},
            'header_comment': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mime_headers': ('django.db.models.fields.TextField', [], {}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['po_projects.Project']"}),
            'version': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        u'po_projects.templatemsg': {
            'Meta': {'object_name': 'TemplateMsg'},
            'flags': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locations': ('django.db.models.fields.TextField', [], {}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'pluralizable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'project_version': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['po_projects.ProjectVersion']"}),
            'python_format': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'po_projects.translationmsg': {
            'Meta': {'object_name': 'TranslationMsg'},
            'catalog': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['po_projects.Catalog']"}),
            'fuzzy': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'pluralizable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'python_format': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['po_projects.TemplateMsg']"})
        }
    }

    complete_apps = ['po_projects']