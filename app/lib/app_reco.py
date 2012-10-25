# coding: utf-8
import json
import urllib2
from app.const import *

from app.models import *

result = '{"@udid":"841c75fb9ccbd89993cb13cc9a997975d664d4e9","@type":"Recommendations","@version":"1.0","@generatedDate":"8/29/12 8:00 PM","recommendation":[{"@publisherName":"cyberagent inc","@description":"","@appPrice":"0","@appName":"FreeAppKing","@appIconUrl":"http://ad.flurry.com/getIcon.do?id=0","@actionUrl":"http://ad.flurry.com/manualGetIPhoneApp.do?v=1&e=E8noM_Fhg7o2YNs6hYHFX9ihWUiKtvIhmu1Cq98851X9SMkFnZQ7GUIcJWFxWslAKWFDJRCidAk2ABvBZ45nEzsFVyoFSuGeL36WDhP-s41UOdctL0EyxzEcuDOj2JexcdHOqrdgNE7-FFwYkpR9seePLBpgA_KIe1bKEYLrAi-eWkzsftVIM2TsZQZKQJEc"},{"@publisherName":"Zynga Inc.","@description":"Brand new from the makers of the #1-rated Zynga Poker comes Zynga Slots, a one-of-a-kind video slots game!els to win coins and dash across a variety of different exciting and magical worlds. Join hot jackpots with your friends, then get lucky and grab the cash before they do!at a tiODE every time you play for higher r favorite machines for more lines and bets!every few minutes, and even more when your frieay now and experience a new spin his application is governed by the Zynga Terms of Service. Collection and use of personal data are subject to Zynga Privacy Policy. Both policies areavailable in the Application License Agreement below as well as at www.zynga.com. Social Networking Service terms may also apply.","@appPrice":"0","@appName":"Zynga Slots","@appIconUrl":"http://ad.flurry.com/getIcon.do?id=5372","@actionUrl":"http://ad.flurry.com/manualGetIPhoneApp.do?v=1&e=Hcnl4H-CK-5mvDPR2IsLT9ihWUiKtvIhmu1Cq98851X9SMkFnZQ7GUIcJWFxWslAKWFDJRCidAk2ABvBZ45nEzsFVyoFSuGeL36WDhP-s41UOdctL0EyxzEcuDOj2JexcdHOqrdgNE7-FFwYkpR9seePLBpgA_KIe1bKEYLrAi-eWkzsftVIM2TsZQZKQJEc"},{"@publisherName":"Zynga Mobile","@description":"More of your friends are playing Words with Friends than ANY other wordNow you can play everybody’s favorite crossword game with your friends and fith Friends’ app is the new Twitter.” – Jos an iPhone or iPod Touch should have this game on their device.” – Touch h Friends is the best word game in the App Store today.” – ased design lets you play up to 20 games simultaneouslyiends, or matchmake instantly with a random d familiar rules that you know ane, or pass and play with someone neaur growing community of millions of players ntions tell you when it’s your turnriends through Facebook and Twitter!ep in touch with loved ones around thyou like Words with Friends, try Chess with Friends also!  iPad users - check out Words with Friends HD!","@appPrice":"0","@appName":"Words With Friends Free and to make this name super","@appIconUrl":"http://ad.flurry.com/getIcon.do?id=1249","@actionUrl":"http://ad.flurry.com/manualGetIPhoneApp.do?v=1&e=zEQ1t1zvP6V3p8EWeYYnEdihWUiKtvIhmu1Cq98851X9SMkFnZQ7GUIcJWFxWslAKWFDJRCidAk2ABvBZ45nEzsFVyoFSuGeL36WDhP-s41UOdctL0EyxzEcuDOj2JexcdHOqrdgNE7-FFwYkpR9seePLBpgA_KIe1bKEYLrAi-eWkzsftVIM2TsZQZKQJEc"},{"@publisherName":"SKYVU PICTURES Inc.","@description":"OVER 15 MILLION BB DOWNLOADS! Like COD with Teddy Btion Game Runner-Upippover 3G or WiFi and stake your claim as the best BATTLE BEAR in the world! BBR is a funny action shooter everyone c ClasivnHUGGst female BATTLE BEown BATTLE BEAR with a massive array of powerful and hilarious primpons and amazing power-ups as you pwn your friends across 4 distinct multi-level maps! Catch all the upcoming updates includming in next updayour sensitivity in PAUSE mOVE: Slide LEFT Thumb over Green Joyst SWITCH WEAPONS: Tap weapons icon in top right cornerns button in bottom cenind special jump pan top cenTHE BB GAZOMBIES (50% OFF SAL YouTube.com US BRING YOU MORE UPDATES! Wntrols with a new fire button. The SkyVu family appreciates your support.","@appPrice":"0","@appName":"Battle Bears Royale","@appIconUrl":"http://ad.flurry.com/getIcon.do?id=4657","@actionUrl":"http://ad.flurry.com/manualGetIPhoneApp.do?v=1&e=15OwIia3qefRm7HTQPciidihWUiKtvIhmu1Cq98851X9SMkFnZQ7GUIcJWFxWslAKWFDJRCidAk2ABvBZ45nEzsFVyoFSuGeL36WDhP-s41UOdctL0EyxzEcuDOj2JexcdHOqrdgNE7-FFwYkpR9seePLBpgA_KIe1bKEYLrAi-eWkzsftVIM2TsZQZKQJEc"}]}'


class App(object):
    def __init__(self, args_dict, has_udid):
        self.description = args_dict.get(kDESCRIPTION)
        self.publisher = args_dict.get(kPUBLISHER)
        self.app_name = args_dict.get(kAPP_NAME)
        self.app_id = args_dict.get(kAPP_NAME).replace(' ', '-')
        self.app_price = args_dict.get(kAPP_PRICE)
        self.icon_url = args_dict.get(kICON_URL)
        self.has_udid = True
        if has_udid:
            self.action_url = args_dict.get(kACTION_URL)
        else:
            self.has_udid = False
            self.action_url = kDEFAULT_ACTION_URL


def get_recommendations(ip_addr, udid=None):
    has_udid = True
    if not udid:
        udid = kUDID
        has_udid = False
    url = 'http://api.flurry.com/appCircle/getRecommendations?apiAccessCode=%s&apiKey=%s&udid=%s&platform=%s&ipAddress=%s' % (kACCESS_CODE, kAPI_KEY, udid, kPLATFORM, ip_addr)
    headers = {'Accept' : 'application/json'}
    request = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(request)
    result = response.read()
    result_json = json.loads(result)
    return_list = []
    try:
        for i in result_json['recommendation']:
            a = App(i, has_udid)
            return_list.append(a)
    except:
        pass
    return return_list
    

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
    
