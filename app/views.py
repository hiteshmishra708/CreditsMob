from django.http import HttpResponse
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from django.middleware.csrf import get_token
from django.template import Context, loader
from django.template import RequestContext, Template
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core import serializers
from django.http import HttpResponseRedirect
import json
import hashlib
from ipware.ip import get_ip_address_from_request

import pyapns.client
import time
import logging
from operator import itemgetter
import urllib2
import urllib
from app import const

from app.lib.app_reco import get_balance, too_many_downloads, get_all_recos
from app.lib.db import *
from django.core.mail import send_mail
import datetime

from app.models import AppHistory, Balance, User
from throttle.decorators import throttle


def __is_ios__(request):
    return False
    user_agent = request.META['HTTP_USER_AGENT']
    if ('Mozilla' not in user_agent and 'Safari' not in user_agent) and ('Profile' not in user_agent):
        print '00' * 40
        print 'in Mozilla or safari : ' , user_agent
        return False
    else:
        print 'user agent is good , ' , user_agent
        print '00' * 40
    if ('iPhone' in user_agent or 'iPad' in user_agent or 'iPod' in user_agent or 'Profile/1.0' in user_agent) and not 'CriOS' in user_agent:
        return True
    return False

def not_allowed(request):
    t = loader.get_template('not_allowed.html')
    c = Context({})
    response = HttpResponse(t.render(c))
    return response
    
@throttle(zone='default')
def index(request):
    is_ios = __is_ios__(request)
    if not is_ios:
        return HttpResponseRedirect('/not_allowed')
    return HttpResponseRedirect('/m')
    
@throttle(zone='default')
def home(request, display=None):
    is_ios = __is_ios__(request)
    if not is_ios:
        return HttpResponseRedirect('/not_allowed')
    print '*' * 40
    print request
    print '*' * 40
    csrf_token = get_token(request)
    ip_addr = request.META['HTTP_X_FORWARDED_FOR']
    udid = None
    user = None
    email = None
    user_id = None
    class_name = None
    show_facebook= True
    udid_hash = None
    if request.COOKIES.has_key(const.kAPP_USER_COOKIE):
        user = get_user_using_id(request.COOKIES.get(const.kAPP_USER_COOKIE))
    elif request.GET.get(const.kAPP_USER_ID):
        user = get_user_using_hash(request.GET.get(const.kAPP_USER_ID))
    else:
        user = None

    if user:
        udid = user.udid
        udid_hash = user.udid_hash

    if udid:
        email = user.email
        user_id = user.id

        if request.GET.get('post_id'):
            to_credit = social_shared(user_id, const.kSHARED_FACEBOOK)
            if to_credit:
                add_balance_to_udid(udid,200)
        if email:
            class_name = 'has_email'
            if not user.email_verified:
                class_name = 'not_verified'
        else:
            class_name = 'no_email'
        show_facebook = to_show_social(user_id, const.kSHARED_FACEBOOK) 
    else:
        class_name = 'no_udid'
    balance = get_balance(user)
    rewards = get_rewards()
    t = loader.get_template('index.html')
    c = Context({'balance' : balance, 'rewards' : rewards, 'email' : email, 'class_name' : class_name , 'user_id': user_id, 'show_facebook' : show_facebook, 'udid_hash': udid_hash})
    response = HttpResponse(t.render(c))
    #if user:
        #max_age = 365*24*60*60
        #expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
        #response.set_cookie(const.kAPP_USER_COOKIE, user.id, max_age=max_age, expires=expires) 
    return response


def recos(request):
    udid = None
    user = None
    email = None
    user_id = None
    ip_addr = request.META['HTTP_X_FORWARDED_FOR']
    udid_hash = request.GET.get('udid_hash')
    udid_hash = udid_hash.strip()
    if udid_hash == "none":
        class_name = "no_udid"
        pass
    else:
        user = get_user_using_hash(udid_hash)
    if user:
        udid = user.udid
        user_id = user.id

        class_name = 'has_udid'
        if user.email and not user.email_verified:
            class_name = 'not_verified'
            email = user.email
        elif not user.email:
            class_name = 'no_email'
        #ip_addr = '195.202.253.169'
        users_for_ip = AppHistory.objects.filter(ip_addr=ip_addr).values_list('user_id', flat=True).distinct()
        if len(users_for_ip) > 0 and user.id not in users_for_ip:
            return HttpResponse('We cannot activate your account at this time. Please email <a href="mailto:support@creditsmob.com">support@creditsmob.com</a> for more details.')
        else:
            print 'keep going'
    data = get_all_recos(ip_addr, udid, user)
    too_many = too_many_downloads(user)
    try:
        c = Context({'data' : data, 'too_many' : too_many, 'class_name' : class_name, 'email' : email, 'user_id' : user_id})
        t = loader.get_template('reco.html')
        c.update(csrf(request))
        response = HttpResponse(t.render(c))
    except Exception, e:
        print 'exception :', e
    return response




@csrf_exempt
def apicallback(request):
    if not request.GET.get('udid'):
        return HttpResponse(False)
    try:
        udid = request.GET.get('udid')
        ip_addr = request.GET.get('addr')
        sec_code = request.GET.get('sec')
        app_name = request.GET.get('appName')
        icon_url = request.GET.get('iconUrl')
        balace = add_balance_to_udid(udid, sec_code = sec_code, app_name=app_name, icon_url=icon_url, ip_addr=ip_addr, sec_check=True)
    except Exception, e:
        print 'EXCEPTIOn : ', e
        print '---' * 40
    return HttpResponse(True) 


def sponsor_callback(request):
    try: 
        uid = request.GET.get('uid')
        credits = request.GET.get('amount')
        token = request.GET.get('sid')
        a = hashlib.sha1()
        a.update(const.kSPONSOR_TOKEN + uid + credits)
        chk_sum = a.hexdigest()
        if token == chk_sum:
            user = User.objects.get(id=int(uid))
            add_balance_to_udid(user.udid, credits = int(credits))
        return HttpResponse(True)
    except Exception, e:
        print 'EXEPOTIN in CALLBACk  ', e



def tos(request):
    is_ios = __is_ios__(request)
    if not is_ios:
        return HttpResponseRedirect('/not_allowed')
    t = loader.get_template('tos.html')
    c = Context({})
    response = HttpResponse(t.render(c))
    return response
    



def ajax_put_email(request):
    print '*' * 40
    print 'in ajax'
    if not request.is_ajax():
        return HttpResponse(False)
    
    email = request.POST.get('email')
    user_id = request.POST.get('userId')
    if not email and not user_id: 
        return HttpResponse(False)

    user = put_and_send_email_for_user(user_id, email)

    if user:
        return HttpResponse("We have sent an activation link to %s. Please click on that link to verify the email address is correct. Upon verification, you will need to come back to redeem your reward." % email)
    return HttpResponse(False)


def activation(request, activation_code):
    try:
        user = User.objects.get(email_activation=activation_code)
        user.email_verified = True
        user.save()
        template = 'activation_success.html'
    except Exception, e: 
        print 'exception : ', e
        template = 'activation_error.html'
    t = loader.get_template(template)
    c = Context({})
    response = HttpResponse(t.render(c))
    return response
    
@throttle(zone='ajax')
def ajax_send_reward(request):
    if not request.is_ajax():
        return HttpResponse(False)
    email = request.POST.get('email')
    user_id = request.POST.get('userId')
    reward_no = request.POST.get('rewardNo')


    #reduce inventory and balance and keep track
    did_reduce, error_or_code, claim = reduce_inventory_and_balance(int(reward_no), int(user_id))
    if not did_reduce:
        return HttpResponse(error_or_code)

    #send email
    send_gift_card(email, error_or_code, claim)
    print 'sending reward '
    return HttpResponse("Congratulations! Enjoy shopping.")


    
def download_csv_balance_file(request):
    filename = 'balance_%s.csv' % int(time.time())
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    bal_rows = Balance.objects.filter(balance__gt = 0)
    balwriter = csv.writer(response)
    balwriter.writerow(['UDID', 'EMAIL', 'BALANCE'])
    for row in bal_rows:
        try:
            user = User.objects.get(id=row.user_id)
            if user.email:
                balwriter.writerow([user.udid, user.email, row.balance])
            else:
                continue
        except:
            continue    
    return response
