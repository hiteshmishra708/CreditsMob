from app.models import User, Balance, Rewards,SocialShared, RewardClaim, SecurityCodes, AppHistory
import hashlib
from app import const
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from datetime import datetime, timedelta


def create_user_by_udid(udid):
    ''' not used '''
    if not udid:
        return
    try:
        user = User.objects.get(udid=udid)
    except User.DoesNotExist:
        user = None
    if user:
        return user
    user = User()
    user.udid = udid
    user.save()
    return user


def put_and_send_email_for_user(user_id, email):
    email = email.lower()
    user = User.objects.get(id=user_id)
    if not user:
        return False
    #if user.email and user.email == email:
    #    return user
    code = get_activation_code(email, user.udid)
    user.email = email
    user.email_activation = code
    user.created_at = datetime.now()
    user.save()
    send_email_activation(user.email, user.email_activation)
    return user


def send_email_activation(email, activation_code):
    active_link = 'http://srajdev.com/activation/%s' % activation_code
    text_template = get_template('activation_email.txt')
    html_template = get_template('activation_email.html')

    data = Context({'email_link': active_link})

    text_content = text_template.render(data)
    html_content = html_template.render(data)

    subject = 'CreditsMob - Please confirm email'
    from_email = 'swapan@swapan.webfactional.com'
    to = [email]
    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
    

def send_gift_card(email, rewards_row, claim_row):
    text_template = get_template('rewards_email.txt')
    html_template = get_template('rewards_email.html')
    img_url = None
    if rewards_row.reward_type in [const.kAMAZON_10, const.kAMAZON_5]:
        img_url = 'http://srajdev.com/media/images/amazon_gift.jpeg'

    data = Context({'request_time' : claim_row.created_at, 'img_url': img_url, 'reward_code': rewards_row.code, 'dollar_worth' : rewards_row.dollar_worth})
    text_content = text_template.render(data)
    html_content = html_template.render(data)

    subject = 'CreditsMob - Your reward'
    from_email = 'swapan@swapan.webfactional.com'
    to = [email]
    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
    



    


def get_activation_code(email, udid):
    email_key = email + '|' + udid + '|' + const.kSECRET
    code = hashlib.md5(email_key).hexdigest()
    return code


def get_user_using_id(user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None
    return user

def get_user_using_hash(hash_id):
    try:
        user = User.objects.get(udid_hash=hash_id)
    except User.DoesNotExist:
        return None
    return user

def add_balance_to_udid(udid, credits=500, ip_addr=None, sec_code=None, app_name=None, icon_url=None):
    user = User.objects.get(udid=udid)
    if not user:
        raise Exception
    should_give_credit = check_for_credits(udid, sec_code)
    if not should_give_credit:
        print 'Not the right security matching code'
        raise Exception
    added_history = add_app_history(user, app_name, icon_url, ip_addr)
    if not added_history:
        print 'already downlaoded app'
        raise Exception
    try:
        balance = Balance.objects.get(user_id=user.id)
    except Balance.DoesNotExist:
        balance = Balance()
        balance.user_id = user.id
        balance.balance = 0
    balance.balance  += credits
    balance.save()
    return balance
        
def check_for_credits(udid, sec_code):
    import hashlib
    sec = '%s|%s|aksjdioew' % (udid, const.kSECRET)
    return sec_code == hashlib.md5(sec).hexdigest()
    #try:
    #    row = SecurityCodes.objects.get(user_id=user.id)
    #    if row.sec_code == sec_code:
    #        return True
    #except:
    #    return False
    #return False
        
def add_app_history(user, app_name, icon_url, ip_addr):
    row = None
    try:
        row = AppHistory.objects.get(user_id=user.id, app_name=app_name)
    except:
        pass
    if row:
        return False
    row = AppHistory()
    row.user_id=user.id
    row.app_name = app_name
    row.icon_url = icon_url
    row.ip_addr = ip_addr
    row.save()
    return True

def get_rewards():
    return_list = []
    for reward_type in const.REWARD_TYPES_LIST:
        rewards = Rewards.objects.filter(active=1).filter(reward_type=reward_type)[:1]
        if rewards:
            return_list.append(rewards[0])
    return return_list
    #for a in rewards:
    #    return_list.append(a.to_dict)
    #return return_list
    
def social_shared(user_id, method):
    try:
        row = SocialShared.objects.get(user_id=user_id, method=method)
        mod_time = row.modified_at.replace(tzinfo=None)
        if (datetime.now() - mod_time)  < timedelta(days=7):
            return False
    except SocialShared.DoesNotExist:
        row = SocialShared()
        row.user_id = user_id
        row.method = method
        row.count = 0
    row.count += 1
    row.save()
    return True


def to_show_social(user_id, method):
    try:
        row = SocialShared.objects.get(user_id=user_id, method=method)
        mod_time = row.modified_at.replace(tzinfo=None)
        if (datetime.now() - mod_time)  < timedelta(days=7):
            return False
    except SocialShared.DoesNotExist:
        pass
    return True

def reduce_inventory_and_balance(reward_no, user_id):
    error = None
    row = Rewards.objects.get(id=reward_no)
    if row.active ==0:
        next_row = Rewards.objects.filter(active=1).filter(reward_type=row.reward_type)[:1]
        if not next_row:
            error = "Sorry we just ran out of this award, Please refresh the page to see the available rewards"
            return False, error
        row = next_row[0]
    row.active = 0
    row.save()
    user = Balance.objects.get(user_id=user_id)
    if user.balance < row.credits_worth:
        error = "Sorry you dont have enough credits to claim this award"
        return False, error, None
    user.balance -= row.credits_worth
    user.save()
    claim = RewardClaim()
    claim.user_id= user_id
    claim.reward_id = row.id
    claim.save()
    code = row.code
    return True, row, claim
