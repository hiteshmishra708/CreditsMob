# coding: utf-8
import json
import urllib2
from app.const import *

from app.models import *
import base64, hashlib, hmac, time, urllib2
from urllib import urlencode, quote_plus
import binascii

import time
import hashlib
from datetime import datetime, timedelta
from django.utils import timezone
from operator import itemgetter


def get_all_recos(ip_addr, udid=None, user=None):
    flurry_recos = get_flurry_recommendations(ip_addr, udid, user)
    sponsor_recos = get_sponsor_reco(ip_addr, udid, user)
    return_list = [] + flurry_recos + sponsor_recos
    return_list = sorted(return_list,key= lambda k:k.credits_worth, reverse=True)
    return return_list

class App(object):
    def __init__(self, args_dict, has_udid):
        self.description = args_dict.get(kDESCRIPTION)
        self.publisher = args_dict.get(kPUBLISHER)
        self.app_name = args_dict.get(kAPP_NAME)
        self.app_id = args_dict.get(kAPP_NAME).replace(' ', '-')
        self.app_price = args_dict.get(kAPP_PRICE)
        self.icon_url = args_dict.get(kICON_URL)
        self.has_udid = True
        self.credits_worth = 500
        if has_udid:
            self.action_url = args_dict.get(kACTION_URL)
        else:
            self.has_udid = False
            self.action_url = kDEFAULT_ACTION_URL




def get_flurry_recommendations(ip_addr, udid=None, user=None):
    has_udid = True
    if not udid:
        udid = kUDID
        has_udid = False
    url = 'http://api.flurry.com/appCircle/getRecommendations?apiAccessCode=%s&apiKey=%s&udid=%s&platform=%s&ipAddress=%s' % (kACCESS_CODE, 'H9WKFJTKJVNTTZV65JW2', udid, kPLATFORM, ip_addr)
    headers = {'Accept' : 'application/json'}
    request = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(request)
    result = response.read()
    result_json = json.loads(result)
    return_list = []
    try:
        for i in result_json['recommendation']:
            try:
                a = App(i, has_udid)
                if udid and user:
                    a = add_custom_params(a, udid, user, ip_addr)
                return_list.append(a)
            except Exception, e:
                print 'FAILED TO GET A RECO : '
    except Exception, e:
        print 'ECEPTION : ', e
        pass
    return return_list
   

def add_custom_params(row, udid, user, ip_addr):
    sec = '%s|%s|aksjdioew' % (udid, kSECRET)
    code = hashlib.md5(sec).hexdigest()
    row.action_url = row.action_url + '&c_user=' + user.udid_hash + '&c_addr=' + ip_addr + '&c_sec=' + code + '&c_appName=' + row.app_name + '&c_iconUrl=' + row.icon_url + '&c_credits=500'
    row.action_url = row.action_url[:56] + 'thisisnotcoolbuddy' + row.action_url[56:]
    return row
     

def get_balance(user):
    balance = 0
    if not user:
        return 0
    try:
        balance_obj = Balance.objects.get(user_id = user.id)
        balance = balance_obj.balance
    except Balance.DoesNotExist:
        balance = 0
    return balance
    

def too_many_downloads(user):
    if not user:
        return False
    else:
        try:
            date_comp = timezone.now() - timedelta(minutes=5)
            count = AppHistory.objects.filter(created_at__gte=date_comp).filter(user_id=user.id).count()
            if count >= 3:
                return True
            return False
        except Exception, e:
            print 'in exception : ', e
            return False

class SponsorApp(object):
    def __init__(self, args_dict, has_udid):
        self.description = args_dict.get('teaser')
        self.app_name = args_dict.get('title')
        self.app_id = args_dict.get('offer_id')
        self.icon_url = args_dict.get('thumbnail').get('lowres')
        self.has_udid = True
        self.credits_worth = args_dict.get('payout')
        if has_udid:
            self.action_url = args_dict.get('link')
        else:
            self.has_udid = False
            self.action_url = kDEFAULT_ACTION_URL

def get_sponsor_reco(ip_addr, udid=None, user=None):
    has_udid = True
    if not udid:
        has_udid = False
    url = get_sponsor_url(ip_addr, udid, user)
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    result = response.read()
    result_json = json.loads(result)
    return_list = []
    try:
        count = result_json['count']
        if count > 0:
            try:
                offers = result_json['offers']
                for offer in offers:
                    valid_offer = False
                    is_free = False
                    for o_type in offer['offer_types']:
                        if o_type['offer_type_id'] in [101, 113]:
                            valid_offer = True
                        if o_type['offer_type_id'] in [112]:
                            is_free = True
                    if is_free and valid_offer:
                        a = SponsorApp(offer, has_udid)
                        return_list.append(a)
            except Exception, e:
                print 'malformed sponsor pay result : ', e
    except Exception , e:
        print 'something went wrong in sponsor result : ', result_json
    return return_list



def get_sponsor_url(ip_addr, udid=None, user=None):
    has_udid = True
    if not udid:
        udid = kUDID
        has_udid = False
    if user:
        user_id = user.id
    else:
        user_id = 1
    base_url = 'http://api.sponsorpay.com/feed/v1/offers.json'
    base_params = {'appid' : 8983,
                    'uid' : user_id,
                    'locale' : 'en',
                    'os_version' : '5.1.1',
                    'timestamp' : int(time.time()),
                    'ip' : ip_addr,
                    'offer_types' : '101,112,113',
                    'device_id' : udid}

    api_key = 'c30202a02aefbb621899da8f0a05e68a4d4c0ac2'

    keys = base_params.keys()
    keys.sort()

    values = map(base_params.get, keys)
    base_string = urlencode(zip(keys,values))
    base_string = base_string.replace('%2C' , ',')

    url_string = '%s&%s' %(base_string, api_key)


    a = hashlib.sha1()
    a.update(url_string)
    signature = a.hexdigest()

    full_url = '%s?%s&hashkey=%s' %(base_url, base_string, signature)
    return full_url
