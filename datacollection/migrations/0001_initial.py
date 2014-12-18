from south.db import db
from django.db import models
from datacollection.models import *

class Migration:

    def forwards(self, orm):

        # Adding model 'Conditions'
        db.create_table('datacollection_conditions', (
            ('id', orm['datacollection.Conditions:id']),
            ('name', orm['datacollection.Conditions:name']),
        ))
        db.send_create_signal('datacollection', ['Conditions'])

        # Adding model 'Datasets'
        db.create_table('datacollection_datasets', (
            ('id', orm['datacollection.Datasets:id']),
            ('user', orm['datacollection.Datasets:user']),
            ('paper', orm['datacollection.Datasets:paper']),
            ('treatments', orm['datacollection.Datasets:treatments']),
            ('controls', orm['datacollection.Datasets:controls']),
            ('treatment_file', orm['datacollection.Datasets:treatment_file']),
            ('peak_file', orm['datacollection.Datasets:peak_file']),
            ('peak_xls_file', orm['datacollection.Datasets:peak_xls_file']),
            ('summit_file', orm['datacollection.Datasets:summit_file']),
            ('wig_file', orm['datacollection.Datasets:wig_file']),
            ('bw_file', orm['datacollection.Datasets:bw_file']),
            ('bed_graph_file', orm['datacollection.Datasets:bed_graph_file']),
            ('control_bed_graph_file', orm['datacollection.Datasets:control_bed_graph_file']),
            ('conservation_file', orm['datacollection.Datasets:conservation_file']),
            ('conservation_r_file', orm['datacollection.Datasets:conservation_r_file']),
            ('qc_file', orm['datacollection.Datasets:qc_file']),
            ('qc_r_file', orm['datacollection.Datasets:qc_r_file']),
            ('ceas_file', orm['datacollection.Datasets:ceas_file']),
            ('ceas_r_file', orm['datacollection.Datasets:ceas_r_file']),
            ('venn_file', orm['datacollection.Datasets:venn_file']),
            ('seqpos_file', orm['datacollection.Datasets:seqpos_file']),
            ('conf_file', orm['datacollection.Datasets:conf_file']),
            ('log_file', orm['datacollection.Datasets:log_file']),
            ('summary_file', orm['datacollection.Datasets:summary_file']),
            ('dhs_file', orm['datacollection.Datasets:dhs_file']),
            ('date_created', orm['datacollection.Datasets:date_created']),
            ('status', orm['datacollection.Datasets:status']),
            ('comments', orm['datacollection.Datasets:comments']),
        ))
        db.send_create_signal('datacollection', ['Datasets'])

        # Adding model 'Assemblies'
        db.create_table('datacollection_assemblies', (
            ('id', orm['datacollection.Assemblies:id']),
            ('name', orm['datacollection.Assemblies:name']),
            ('pub_date', orm['datacollection.Assemblies:pub_date']),
        ))
        db.send_create_signal('datacollection', ['Assemblies'])

        # Adding model 'Papers'
        db.create_table('datacollection_papers', (
            ('id', orm['datacollection.Papers:id']),
            ('pmid', orm['datacollection.Papers:pmid']),
            ('unique_id', orm['datacollection.Papers:unique_id']),
            ('user', orm['datacollection.Papers:user']),
            ('title', orm['datacollection.Papers:title']),
            ('reference', orm['datacollection.Papers:reference']),
            ('abstract', orm['datacollection.Papers:abstract']),
            ('pub_date', orm['datacollection.Papers:pub_date']),
            ('date_collected', orm['datacollection.Papers:date_collected']),
            ('authors', orm['datacollection.Papers:authors']),
            ('last_auth_email', orm['datacollection.Papers:last_auth_email']),
            ('journal', orm['datacollection.Papers:journal']),
            ('status', orm['datacollection.Papers:status']),
            ('comments', orm['datacollection.Papers:comments']),
        ))
        db.send_create_signal('datacollection', ['Papers'])

        # Adding model 'PaperSubmissions'
        db.create_table('datacollection_papersubmissions', (
            ('id', orm['datacollection.PaperSubmissions:id']),
            ('pmid', orm['datacollection.PaperSubmissions:pmid']),
            ('gseid', orm['datacollection.PaperSubmissions:gseid']),
            ('status', orm['datacollection.PaperSubmissions:status']),
            ('user', orm['datacollection.PaperSubmissions:user']),
            ('ip_addr', orm['datacollection.PaperSubmissions:ip_addr']),
            ('submitter_name', orm['datacollection.PaperSubmissions:submitter_name']),
            ('comments', orm['datacollection.PaperSubmissions:comments']),
        ))
        db.send_create_signal('datacollection', ['PaperSubmissions'])

        # Adding model 'Strains'
        db.create_table('datacollection_strains', (
            ('id', orm['datacollection.Strains:id']),
            ('name', orm['datacollection.Strains:name']),
        ))
        db.send_create_signal('datacollection', ['Strains'])

        # Adding model 'DiseaseStates'
        db.create_table('datacollection_diseasestates', (
            ('id', orm['datacollection.DiseaseStates:id']),
            ('name', orm['datacollection.DiseaseStates:name']),
        ))
        db.send_create_signal('datacollection', ['DiseaseStates'])

        # Adding model 'CellTypes'
        db.create_table('datacollection_celltypes', (
            ('id', orm['datacollection.CellTypes:id']),
            ('name', orm['datacollection.CellTypes:name']),
        ))
        db.send_create_signal('datacollection', ['CellTypes'])

        # Adding model 'CellPops'
        db.create_table('datacollection_cellpops', (
            ('id', orm['datacollection.CellPops:id']),
            ('name', orm['datacollection.CellPops:name']),
        ))
        db.send_create_signal('datacollection', ['CellPops'])

        # Adding model 'UserProfiles'
        db.create_table('datacollection_userprofiles', (
            ('id', orm['datacollection.UserProfiles:id']),
            ('user', orm['datacollection.UserProfiles:user']),
            ('team', orm['datacollection.UserProfiles:team']),
        ))
        db.send_create_signal('datacollection', ['UserProfiles'])

        # Adding model 'TissueTypes'
        db.create_table('datacollection_tissuetypes', (
            ('id', orm['datacollection.TissueTypes:id']),
            ('name', orm['datacollection.TissueTypes:name']),
        ))
        db.send_create_signal('datacollection', ['TissueTypes'])

        # Adding model 'Platforms'
        db.create_table('datacollection_platforms', (
            ('id', orm['datacollection.Platforms:id']),
            ('gplid', orm['datacollection.Platforms:gplid']),
            ('name', orm['datacollection.Platforms:name']),
            ('technology', orm['datacollection.Platforms:technology']),
            ('company', orm['datacollection.Platforms:company']),
            ('experiment_type', orm['datacollection.Platforms:experiment_type']),
        ))
        db.send_create_signal('datacollection', ['Platforms'])

        # Adding model 'CellLines'
        db.create_table('datacollection_celllines', (
            ('id', orm['datacollection.CellLines:id']),
            ('name', orm['datacollection.CellLines:name']),
        ))
        db.send_create_signal('datacollection', ['CellLines'])

        # Adding model 'Samples'
        db.create_table('datacollection_samples', (
            ('id', orm['datacollection.Samples:id']),
            ('user', orm['datacollection.Samples:user']),
            ('paper', orm['datacollection.Samples:paper']),
            ('unique_id', orm['datacollection.Samples:unique_id']),
            ('name', orm['datacollection.Samples:name']),
            ('date_collected', orm['datacollection.Samples:date_collected']),
            ('fastq_file', orm['datacollection.Samples:fastq_file']),
            ('fastq_file_url', orm['datacollection.Samples:fastq_file_url']),
            ('bam_file', orm['datacollection.Samples:bam_file']),
            ('factor', orm['datacollection.Samples:factor']),
            ('platform', orm['datacollection.Samples:platform']),
            ('species', orm['datacollection.Samples:species']),
            ('assembly', orm['datacollection.Samples:assembly']),
            ('description', orm['datacollection.Samples:description']),
            ('cell_type', orm['datacollection.Samples:cell_type']),
            ('cell_line', orm['datacollection.Samples:cell_line']),
            ('cell_pop', orm['datacollection.Samples:cell_pop']),
            ('strain', orm['datacollection.Samples:strain']),
            ('condition', orm['datacollection.Samples:condition']),
            ('disease_state', orm['datacollection.Samples:disease_state']),
            ('tissue_type', orm['datacollection.Samples:tissue_type']),
            ('antibody', orm['datacollection.Samples:antibody']),
            ('curator', orm['datacollection.Samples:curator']),
            ('status', orm['datacollection.Samples:status']),
            ('comments', orm['datacollection.Samples:comments']),
            ('upload_date', orm['datacollection.Samples:upload_date']),
        ))
        db.send_create_signal('datacollection', ['Samples'])

        # Adding model 'Species'
        db.create_table('datacollection_species', (
            ('id', orm['datacollection.Species:id']),
            ('name', orm['datacollection.Species:name']),
        ))
        db.send_create_signal('datacollection', ['Species'])

        # Adding model 'Factors'
        db.create_table('datacollection_factors', (
            ('id', orm['datacollection.Factors:id']),
            ('name', orm['datacollection.Factors:name']),
            ('type', orm['datacollection.Factors:type']),
        ))
        db.send_create_signal('datacollection', ['Factors'])

        # Adding model 'Journals'
        db.create_table('datacollection_journals', (
            ('id', orm['datacollection.Journals:id']),
            ('name', orm['datacollection.Journals:name']),
            ('issn', orm['datacollection.Journals:issn']),
            ('impact_factor', orm['datacollection.Journals:impact_factor']),
        ))
        db.send_create_signal('datacollection', ['Journals'])

        # Adding model 'Antibodies'
        db.create_table('datacollection_antibodies', (
            ('id', orm['datacollection.Antibodies:id']),
            ('name', orm['datacollection.Antibodies:name']),
        ))
        db.send_create_signal('datacollection', ['Antibodies'])



    def backwards(self, orm):

        # Deleting model 'Conditions'
        db.delete_table('datacollection_conditions')

        # Deleting model 'Datasets'
        db.delete_table('datacollection_datasets')

        # Deleting model 'Assemblies'
        db.delete_table('datacollection_assemblies')

        # Deleting model 'Papers'
        db.delete_table('datacollection_papers')

        # Deleting model 'PaperSubmissions'
        db.delete_table('datacollection_papersubmissions')

        # Deleting model 'Strains'
        db.delete_table('datacollection_strains')

        # Deleting model 'DiseaseStates'
        db.delete_table('datacollection_diseasestates')

        # Deleting model 'CellTypes'
        db.delete_table('datacollection_celltypes')

        # Deleting model 'CellPops'
        db.delete_table('datacollection_cellpops')

        # Deleting model 'UserProfiles'
        db.delete_table('datacollection_userprofiles')

        # Deleting model 'TissueTypes'
        db.delete_table('datacollection_tissuetypes')

        # Deleting model 'Platforms'
        db.delete_table('datacollection_platforms')

        # Deleting model 'CellLines'
        db.delete_table('datacollection_celllines')

        # Deleting model 'Samples'
        db.delete_table('datacollection_samples')

        # Deleting model 'Species'
        db.delete_table('datacollection_species')

        # Deleting model 'Factors'
        db.delete_table('datacollection_factors')

        # Deleting model 'Journals'
        db.delete_table('datacollection_journals')

        # Deleting model 'Antibodies'
        db.delete_table('datacollection_antibodies')



    models = {
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'datacollection.antibodies': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'datacollection.assemblies': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pub_date': ('django.db.models.fields.DateField', [], {'blank': 'True'})
        },
        'datacollection.celllines': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'datacollection.cellpops': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'datacollection.celltypes': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'datacollection.conditions': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'datacollection.datasets': {
            'bed_graph_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'bw_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'ceas_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'ceas_r_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'conf_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'conservation_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'conservation_r_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'control_bed_graph_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'controls': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'dhs_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'log_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'paper': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['datacollection.Papers']"}),
            'peak_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'peak_xls_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'qc_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'qc_r_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'seqpos_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '255'}),
            'summary_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'summit_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'treatment_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'treatments': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'venn_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'wig_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'datacollection.diseasestates': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'datacollection.factors': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'other'", 'max_length': '255'})
        },
        'datacollection.journals': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'impact_factor': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'issn': ('django.db.models.fields.CharField', [], {'max_length': '9'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'datacollection.papers': {
            'abstract': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'authors': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'date_collected': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'journal': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['datacollection.Journals']", 'null': 'True', 'blank': 'True'}),
            'last_auth_email': ('django.db.models.fields.EmailField', [], {'default': 'None', 'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'pmid': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'pub_date': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'reference': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'imported'", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'unique_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'datacollection.papersubmissions': {
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'gseid': ('django.db.models.fields.CharField', [], {'max_length': '8', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_addr': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'pmid': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'submitter_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'datacollection.platforms': {
            'company': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'experiment_type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'gplid': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'technology': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'datacollection.samples': {
            'antibody': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['datacollection.Antibodies']", 'null': 'True', 'blank': 'True'}),
            'assembly': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['datacollection.Assemblies']", 'null': 'True', 'blank': 'True'}),
            'bam_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'cell_line': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['datacollection.CellLines']", 'null': 'True', 'blank': 'True'}),
            'cell_pop': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['datacollection.CellPops']", 'null': 'True', 'blank': 'True'}),
            'cell_type': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['datacollection.CellTypes']", 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'condition': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['datacollection.Conditions']", 'null': 'True', 'blank': 'True'}),
            'curator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'curator'", 'null': 'True', 'blank': 'True', 'to': "orm['auth.User']"}),
            'date_collected': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'disease_state': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['datacollection.DiseaseStates']", 'null': 'True', 'blank': 'True'}),
            'factor': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['datacollection.Factors']", 'null': 'True', 'blank': 'True'}),
            'fastq_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'fastq_file_url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'paper': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['datacollection.Papers']", 'null': 'True', 'blank': 'True'}),
            'platform': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['datacollection.Platforms']", 'null': 'True', 'blank': 'True'}),
            'species': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['datacollection.Species']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'imported'", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'strain': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['datacollection.Strains']", 'null': 'True', 'blank': 'True'}),
            'tissue_type': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['datacollection.TissueTypes']", 'null': 'True', 'blank': 'True'}),
            'unique_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'upload_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'datacollection.species': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'datacollection.strains': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'datacollection.tissuetypes': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'datacollection.userprofiles': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'team': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'profile'", 'unique': 'True', 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['datacollection']
