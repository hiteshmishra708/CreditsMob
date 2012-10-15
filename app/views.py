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
import datetime
import urllib2
import urllib
from app import const

from app.lib.app_reco import get_recommendations, get_balance
from app.lib.db import *
from django.core.mail import send_mail



@csrf_exempt
def home(request, display=None):
    ip_addr = request.META['HTTP_X_FORWARDED_FOR']
    udid = None
    user = None
    email = None
    user_id = None
    class_name = None
    if request.COOKIES.has_key(const.kAPP_USER_COOKIE):
        user = get_user_using_id(request.COOKIES.get(const.kAPP_USER_COOKIE))
    if not udid and request.GET.get(const.kAPP_USER_COOKIE):
        user = get_user_using_id(request.GET.get(const.kAPP_USER_COOKIE))

    if user:
        udid = user.udid

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
    else:
        class_name = 'no_udid'
    recos = get_recommendations(ip_addr, udid)
    balance = get_balance(user)
    rewards = get_rewards()
    t = loader.get_template('trial.html')
    c = Context({'data' : recos, 'balance' : balance, 'rewards' : rewards, 'email' : email, 'class_name' : class_name , 'user_id': user_id})
    response = HttpResponse(t.render(c))
    if user:
        response.set_cookie(const.kAPP_USER_COOKIE, user.id) 
    return response


@csrf_exempt
def apicallback(request):
    if not request.GET.get('udid'):
        return HttpResponse(False)
    udid = request.GET.get('udid')
    balace = add_balance_to_udid(udid)
    return HttpResponse(True) 
    

@csrf_exempt
def rewards(request):
    udid = None
    user = None
    has_email = False
    has_udid = False
    email = None
    user_id = None
    if request.COOKIES.has_key(const.kAPP_USER_COOKIE):
        user = get_user_using_id(request.COOKIES.get(const.kAPP_USER_COOKIE))
        udid = user.udid
        has_udid = True
        email = user.email
        user_id = user.id
        if email:
            has_email = True
        else:
            has_email = False
    else:
        user_id = 0
        has_udid = False
    balance = get_balance(user)
    rewards = get_rewards()
    c = Context({'data' : rewards, 'balance' : balance, 'email' : email, 'has_udid' : has_udid, 'has_email' : has_email , 'user_id' : user_id})
    t = loader.get_template('rewards.html')
    response = HttpResponse(t.render(c))
    return response

@csrf_exempt
def test(request):
    print '-' * 40
    try:
        for k,v in request.POST.iteritems():
            print 'key : ', open(k).read()
            print 'value:', open(v).read()
    except Exception, e:
        print 'exception :', e
    #return HttpResponseRedirect("/trial")
    return HttpResponse(True)


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
        return HttpResponse("We have sent an activation link to %s (comes from previous page). Please click on that link to verify the email address is correct. Upon verification, you will need to come back to redeem your reward." % email)
    return HttpResponse(False)


@csrf_exempt
def activation(request, activation_code):
    try:
        user = User.objects.get(email_activation=activation_code)
    except User.DoesNotExist: 
        return HttpResponse('Sorry we could not find your email in our system')
    user.email_verified = True
    user.save()
    return HttpResponse('Congratulations. Your email address has now been verified.')
    

@csrf_exempt
def ajax_send_reward(request):
    email = request.POST.get('email')
    user_id = request.POST.get('userId')
    reward_no = request.POST.get('rewardNo')

    print 'in ajax : ' , email, user_id, reward_no

    #reduce inventory and balance and keep track
    did_reduce, error_or_code = reduce_inventory_and_balance(int(reward_no), int(user_id))
    if not did_reduce:
        return HttpResponse(error)

    #send email
    send_mail('Your Reward', 'Your reward code is : %s' % error_or_code, 'swapan@swapan.webfactional.com', [email])
    return HttpResponse("Congratulations! You just just calimed an offer")


    



