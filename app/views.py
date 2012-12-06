from django.http import HttpResponse
from django.template import Context, loader
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.http import HttpResponseRedirect
import json

import pyapns.client
import time
import logging
from operator import itemgetter
import urllib2
import urllib
from app import const

from app.lib.app_reco import get_recommendations, get_balance
from app.lib.db import *
from django.core.mail import send_mail
import datetime



def __is_ios__(request):
    return True
    user_agent = request.META['HTTP_USER_AGENT']
    if ('iPhone' in user_agent or 'iPad' in user_agent or 'iPod' in user_agent or 'Profile/1.0' in user_agent) and not 'CriOS' in user_agent:
        return True
    return False

@csrf_exempt
def not_allowed(request):
    t = loader.get_template('not_allowed.html')
    c = Context({})
    response = HttpResponse(t.render(c))
    return response
    
@csrf_exempt
def index(request):
    is_ios = __is_ios__(request)
    if not is_ios:
        return HttpResponseRedirect('/not_allowed')
    return HttpResponseRedirect('/m')
    

@csrf_exempt
def home(request, display=None):
    is_ios = __is_ios__(request)
    if not is_ios:
        return HttpResponseRedirect('/not_allowed')
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
    if user:
        max_age = 365*24*60*60
        expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
        response.set_cookie(const.kAPP_USER_COOKIE, user.id, max_age=max_age, expires=expires) 
    return response


@csrf_exempt
def recos(request):
    udid = None
    user = None
    ip_arrd = ip_addr = request.META['HTTP_X_FORWARDED_FOR']
    udid_hash = request.GET.get('udid_hash')
    udid_hash = udid_hash.strip()
    if udid_hash == "none":
        pass
    else:
        user = get_user_using_hash(udid_hash)
    if user:
        udid = user.udid
    data = get_recommendations(ip_addr, udid, user)
    c = Context({'data' : data})
    t = loader.get_template('reco.html')
    response = HttpResponse(t.render(c))
    return response




@csrf_exempt
def apicallback(request):
    print '*' * 40
    print 'in api callback : ',
    print request
    print '*' * 40
    if not request.GET.get('udid'):
        return HttpResponse(False)
    try:
        udid = request.GET.get('udid')
        ip_addr = request.GET.get('addr')
        sec_code = request.GET.get('sec')
        app_name = request.GET.get('appName')
        icon_url = request.GET.get('iconUrl')
        balace = add_balance_to_udid(udid, sec_code = sec_code, app_name=app_name, icon_url=icon_url)
    except Exception, e:
        print 'EXCEPTIOn : ', e
        print '---' * 40
    return HttpResponse(True) 


@csrf_exempt
def tos(request):
    is_ios = __is_ios__(request)
    if not is_ios:
        return HttpResponseRedirect('/not_allowed')
    t = loader.get_template('tos.html')
    c = Context({})
    response = HttpResponse(t.render(c))
    return response
    



@csrf_exempt
def ajax_put_email(request):
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


@csrf_exempt
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
    

@csrf_exempt
def ajax_send_reward(request):
    if not request.is_ajax():
        return HttpResponse(False)
    email = request.POST.get('email')
    user_id = request.POST.get('userId')
    reward_no = request.POST.get('rewardNo')


    #reduce inventory and balance and keep track
    did_reduce, error_or_code, claim = reduce_inventory_and_balance(int(reward_no), int(user_id))
    if not did_reduce:
        return HttpResponse(error)

    #send email
    send_gift_card(email, error_or_code, claim)
    return HttpResponse("Congratulations! Enjoy shopping.")


    



