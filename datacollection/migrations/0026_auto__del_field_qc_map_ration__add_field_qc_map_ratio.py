# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Qc.map_ration'
        db.delete_column(u'datacollection_qc', 'map_ration')

        # Adding field 'Qc.map_ratio'
        db.add_column(u'datacollection_qc', 'map_ratio',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Qc.map_ration'
        db.add_column(u'datacollection_qc', 'map_ration',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True),
                      keep_default=False)

        # Deleting field 'Qc.map_ratio'
        db.delete_column(u'datacollection_qc', 'map_ratio')


    models = {
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'datacollection.aliases': {
            'Meta': {'object_name': 'Aliases'},
            'factor': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'aliases'", 'null': 'True', 'blank': 'True', 'to': u"orm['datacollection.Factors']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'datacollection.antibodies': {
            'Meta': {'object_name': 'Antibodies'},
            'aliases': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'new'", 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'datacollection.assemblies': {
            'Meta': {'object_name': 'Assemblies'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'pub_date': ('django.db.models.fields.DateField', [], {'blank': 'True'})
        },
        u'datacollection.celllines': {
            'Meta': {'object_name': 'CellLines'},
            'aliases': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'new'", 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'datacollection.cellpops': {
            'Meta': {'object_name': 'CellPops'},
            'aliases': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'new'", 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'datacollection.celltypes': {
            'Meta': {'object_name': 'CellTypes'},
            'aliases': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'new'", 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'datacollection.conditions': {
            'Meta': {'object_name': 'Conditions'},
            'aliases': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'new'", 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'datacollection.datasets': {
            'Meta': {'object_name': 'Datasets'},
            'ceas_file': ('django.db.models.fields.files.FileField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'ceas_r_file': ('django.db.models.fields.files.FileField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'ceas_xls_file': ('django.db.models.fields.files.FileField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'conf_file': ('django.db.models.fields.files.FileField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'conservation_file': ('django.db.models.fields.files.FileField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'conservation_r_file': ('django.db.models.fields.files.FileField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'cont_bw_file': ('django.db.models.fields.files.FileField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'conts': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'CONTS'", 'default': 'None', 'to': u"orm['datacollection.Samples']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'cor_pdf_file': ('django.db.models.fields.files.FileField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'cor_r_file': ('django.db.models.fields.files.FileField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'dhs_file': ('django.db.models.fields.files.FileField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'log_file': ('django.db.models.fields.files.FileField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'paper': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['datacollection.Papers']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'peak_file': ('django.db.models.fields.files.FileField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'peak_xls_file': ('django.db.models.fields.files.FileField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'qc': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['datacollection.Qc']", 'null': 'True', 'blank': 'True'}),
            'rep_cont_bw': ('django.db.models.fields.files.FileField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'rep_treat_bw': ('django.db.models.fields.files.FileField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'rep_treat_peaks': ('django.db.models.fields.files.FileField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'rep_treat_summits': ('django.db.models.fields.files.FileField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'seqpos_file': ('django.db.models.fields.files.FileField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '255'}),
            'summary_file': ('django.db.models.fields.files.FileField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'summit_file': ('django.db.models.fields.files.FileField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'treat_bw_file': ('django.db.models.fields.files.FileField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'treats': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'TREATS'", 'symmetrical': 'False', 'to': u"orm['datacollection.Samples']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'venn_file': ('django.db.models.fields.files.FileField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'})
        },
        u'datacollection.diseasestates': {
            'Meta': {'object_name': 'DiseaseStates'},
            'aliases': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'new'", 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'datacollection.factors': {
            'Meta': {'object_name': 'Factors'},
            'comments': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'new'", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'datacollection.journals': {
            'Meta': {'object_name': 'Journals'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'impact_factor': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True'}),
            'issn': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '9', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'datacollection.papers': {
            'Meta': {'object_name': 'Papers'},
            'abstract': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'authors': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'date_collected': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'journal': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['datacollection.Journals']", 'null': 'True', 'blank': 'True'}),
            'lab': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'last_auth_email': ('django.db.models.fields.EmailField', [], {'default': 'None', 'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'pmid': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'pub_date': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'pub_summary': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'reference': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'imported'", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'unique_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'datacollection.papersubmissions': {
            'Meta': {'object_name': 'PaperSubmissions'},
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'gseid': ('django.db.models.fields.CharField', [], {'max_length': '8', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_addr': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'pmid': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'submitter_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'datacollection.platforms': {
            'Meta': {'object_name': 'Platforms'},
            'company': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'experiment_type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'gplid': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'new'", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'technology': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'datacollection.qc': {
            'Meta': {'object_name': 'Qc'},
            'dhs': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'fastqc': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'frip': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'map_ratio': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'mapped': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'motif': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'pbc': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'peaks': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'qc10': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'qc9': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        },
        u'datacollection.samples': {
            'Meta': {'object_name': 'Samples'},
            'antibody': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'antibody'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['datacollection.Antibodies']", 'blank': 'True', 'null': 'True'}),
            'assembly': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['datacollection.Assemblies']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'bam_file': ('django.db.models.fields.files.FileField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'cell_line': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['datacollection.CellLines']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'cell_pop': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['datacollection.CellPops']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'cell_type': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['datacollection.CellTypes']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'condition': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['datacollection.Conditions']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'curator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'curator'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['auth.User']", 'blank': 'True', 'null': 'True'}),
            'dc_collect_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'dc_upload_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'disease_state': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['datacollection.DiseaseStates']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'factor': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['datacollection.Factors']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'fastq_file': ('django.db.models.fields.files.FileField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'fastq_file_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'geo_last_update_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'geo_release_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'other_ids': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'paper': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['datacollection.Papers']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'platform': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['datacollection.Platforms']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            're_check': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'series_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'species': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['datacollection.Species']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'strain': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['datacollection.Strains']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'tissue_type': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['datacollection.TissueTypes']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'unique_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'datacollection.species': {
            'Meta': {'object_name': 'Species'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'datacollection.strains': {
            'Meta': {'object_name': 'Strains'},
            'aliases': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'new'", 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'datacollection.tissuetypes': {
            'Meta': {'object_name': 'TissueTypes'},
            'aliases': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'new'", 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'datacollection.userprofiles': {
            'Meta': {'object_name': 'UserProfiles'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'team': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'profile'", 'unique': 'True', 'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['datacollection']