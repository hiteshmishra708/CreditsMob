from django.db import models

# Create your models here.

class User(models.Model):
    udid = models.CharField(max_length=250)
    email = models.CharField(max_length=250, null=True)
    email_activation = models.CharField(max_length=250, null=True)
    email_verified = models.BooleanField(default=False)
    udid_hash = models.CharField(max_length=500)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return unicode_class(self)

    def to_dict(self):
        return convert_to_dict(self)


class SecurityCodes(models.Model):
    user_id = models.IntegerField()
    sec_code = models.CharField(max_length=500)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return unicode_class(self)

    def to_dict(self):
        return convert_to_dict(self)


class AppHistory(models.Model):
    user_id = models.IntegerField()
    app_name = models.CharField(max_length=500)
    icon_url = models.CharField(max_length=500)
    ip_addr = models.CharField(max_length=500)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return unicode_class(self)

    def to_dict(self):
        return convert_to_dict(self)

class SocialShared(models.Model):
    user_id = models.IntegerField()
    method = models.IntegerField()
    count = models.IntegerField(default=1)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return unicode_class(self)

    def to_dict(self):
        return convert_to_dict(self)


class Balance(models.Model):
    user_id = models.IntegerField()
    balance = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return unicode_class(self)

    def to_dict(self):
        return convert_to_dict(self)


class Rewards(models.Model):
    name = models.CharField(max_length=250)
    desc = models.CharField(max_length=250, null=True)
    credits_worth = models.IntegerField()
    api_url = models.CharField(max_length=500, null=True)
    inventory = models.IntegerField(null=True)
    image_url = models.CharField(max_length=250, null=True)
    active = models.BooleanField(default=True)
    dollar_worth = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    code = models.CharField(max_length=250)
    reward_type = models.IntegerField()

    def __unicode__(self):
        return unicode_class(self)

    def to_dict(self):
        return convert_to_dict(self)


class RewardClaim(models.Model):
    user_id = models.IntegerField()
    reward_id = models.IntegerField()
    claim_code = models.CharField(max_length=256, null=True)
    request_id= models.CharField(max_length=256, null=True)
    response_id= models.CharField(max_length=256, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return unicode_class(self)

    def to_dict(self):
        return convert_to_dict(self)

def convert_to_dict(obj):
    return obj.__dict__

def unicode_class(obj):
    s = ''
    for k,v in obj.__dict__.items():
        s += ('%s: %s\n' % (k,v))
    return s
