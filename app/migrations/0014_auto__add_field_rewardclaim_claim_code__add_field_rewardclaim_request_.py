# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'RewardClaim.claim_code'
        db.add_column('app_rewardclaim', 'claim_code',
                      self.gf('django.db.models.fields.CharField')(max_length=256, null=True),
                      keep_default=False)

        # Adding field 'RewardClaim.request_id'
        db.add_column('app_rewardclaim', 'request_id',
                      self.gf('django.db.models.fields.CharField')(max_length=256, null=True),
                      keep_default=False)

        # Adding field 'RewardClaim.response_id'
        db.add_column('app_rewardclaim', 'response_id',
                      self.gf('django.db.models.fields.CharField')(max_length=256, null=True),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'RewardClaim.claim_code'
        db.delete_column('app_rewardclaim', 'claim_code')

        # Deleting field 'RewardClaim.request_id'
        db.delete_column('app_rewardclaim', 'request_id')

        # Deleting field 'RewardClaim.response_id'
        db.delete_column('app_rewardclaim', 'response_id')

    models = {
        'app.apphistory': {
            'Meta': {'object_name': 'AppHistory'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'app_name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'icon_url': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_addr': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user_id': ('django.db.models.fields.IntegerField', [], {})
        },
        'app.balance': {
            'Meta': {'object_name': 'Balance'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'balance': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user_id': ('django.db.models.fields.IntegerField', [], {})
        },
        'app.rewardclaim': {
            'Meta': {'object_name': 'RewardClaim'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'claim_code': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'request_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True'}),
            'response_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True'}),
            'reward_id': ('django.db.models.fields.IntegerField', [], {}),
            'user_id': ('django.db.models.fields.IntegerField', [], {})
        },
        'app.rewards': {
            'Meta': {'object_name': 'Rewards'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'api_url': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'credits_worth': ('django.db.models.fields.IntegerField', [], {}),
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True'}),
            'dollar_worth': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_url': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True'}),
            'inventory': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'reward_type': ('django.db.models.fields.IntegerField', [], {})
        },
        'app.securitycodes': {
            'Meta': {'object_name': 'SecurityCodes'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'sec_code': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'user_id': ('django.db.models.fields.IntegerField', [], {})
        },
        'app.socialshared': {
            'Meta': {'object_name': 'SocialShared'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'count': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.IntegerField', [], {}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user_id': ('django.db.models.fields.IntegerField', [], {})
        },
        'app.user': {
            'Meta': {'object_name': 'User'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True'}),
            'email_activation': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True'}),
            'email_verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'udid': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'udid_hash': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        }
    }

    complete_apps = ['app']