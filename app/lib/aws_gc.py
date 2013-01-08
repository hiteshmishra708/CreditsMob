import base64, hashlib, hmac, time, urllib2
from urllib import urlencode, quote_plus
import binascii
from app import const
import random
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup


def get_amazon_url(action, message_type, params):
    base_url = const.AMAZON_BASE_URL

    base_params= {
        'Action':  action,
        'AWSAccessKeyId' : const.AWS_ACCESS_KEY_ID,
        'MessageHeader.contentVersion' : '2008-01-01',
        'MessageHeader.messageType': message_type,
        'MessageHeader.recipientId' : 'AMAZON',
        'MessageHeader.retryCount' : '0',
        'MessageHeader.sourceId' : const.AMAZON_SOURCE_ID,
        'SignatureMethod' : 'HmacSHA256',
        'SignatureVersion' : '2',
        'Version' : '2008-01-01'}

    base_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    url_params = dict(base_params.items()+ params.items())
    
    keys = url_params.keys()
    keys.sort()

    values = map(url_params.get, keys)

    url_string = urlencode(zip(keys,values))

    string_to_sign = "GET\n%s\n/\n%s" % (const.AMAZON_SIGN_URL, url_string)

    signature = hmac.new(
        key=const.AWS_SECRET_ACCESS_KEY,
        msg=string_to_sign,
        digestmod=hashlib.sha256).digest()

    signature = base64.encodestring(signature).strip()

    urlencoded_signature = quote_plus(signature)

    url_string += "&Signature=%s" % urlencoded_signature

    return base_url + '?' + url_string

def health_check():
    action = 'HealthCheck'
    message_type = 'HealthCheckRequest'

    params = {}
    url = get_amazon_url(action, message_type, params)
    res = make_request(url)

    print res


def create_amazon_gc(value = 1.0, gc_creation_id=None):
    action = 'CreateGiftCard'
    message_type = 'CreateGiftCardRequest'

    random_id = ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(14))

    if not gc_creation_id:
        gc_creation_id = '%s%s' % (const.AMAZON_SOURCE_ID, random_id)

    params = {'gcCreationRequestId' : gc_creation_id,
              'gcValue.amount': value,
              'gcValue.currencyCode' : 'USD'}

    url = get_amazon_url(action, message_type, params)
    res = make_request(url)
    success, info_dict = parse_aws_res(res,action)
    if success:
        print 'info dict', info_dict
        return True, info_dict
    return False, ''


def cancel_amazon_gc(request_id, response_id):
    action = 'CancelGiftCard'
    message_type = 'CancelGiftCardRequest'

    params = {'gcCreationRequestId' : request_id,
              'gcCreationResponseId' : response_id}

    url = get_amazon_url(action, message_type, params)
    res = make_request(url)
    success, info_dict = parse_aws_res(res, action)
    print 'info dict : ', info_dict
    if success:
        return True
    return False
    

def void_amazon_gc(request_id):
    action = 'VoidGiftCardCreation'
    message_type = 'VoidGiftCardCreationRequest'

    params = {'gcCreationRequestId' : request_id}

    url = get_amazon_url(action, message_type, params)
    res = make_request(url)
    success, info_dict = parse_aws_res(res, action)
    print 'info dict : ', info_dict
    if success:
        return True
    return False



def make_request(url):
    a = urllib2.Request(url)
    response = urllib2.urlopen(a)
    res = response.read()
    return res


def parse_aws_res(res, action='CreateGiftCard'):
    a = BeautifulStoneSoup(res)
    if action == 'CreateGiftCard':
        error = a.creategiftcardresponse.status.statuscode.string
    if action == 'CancelGiftCard':
        error = a.cancelgiftcardresponse.status.statuscode.string
    if action == 'VoidGiftCardCreation':
        error = a.voidgiftcardcreationresponse.status.statuscode.string
    return_dict = {}
    success = False
    if error == 'SUCCESS':
        success = True
        if action == 'CreateGiftCard':
            request_id = a.creategiftcardresponse.gccreationrequestid.string
            response_id = a.creategiftcardresponse.gccreationresponseid.string
            claim_code = a.creategiftcardresponse.gcclaimcode.string
            return_dict = {const.kREQUEST_ID : request_id,
                        const.kREPONSE_ID : response_id,
                        const.kCLAIM_CODE : claim_code}
        if action == 'CancelGiftCard':
            request_id = a.cancelgiftcardresponse.gccreationrequestid.string
            response_id = a.cancelgiftcardresponse.gccreationresponseid.string
            return_dict = {const.kREQUEST_ID : request_id,
                        const.kREPONSE_ID : response_id}
        if action == 'VoidGiftCardCreation':
            request_id = a.voidgiftcardcreationresponse.gccreationrequestid.string
            return_dict = {const.kREQUEST_ID : request_id}
    else:
        success = False
        error_code = a.creategiftcardresponse.errorcode
        error_info = a.creategiftcardresponse.statusmessage
        return_dict = {const.kERROR_CODE : error_code, const.kERROR_MESSGAE : error_info}
    return success, return_dict

    
