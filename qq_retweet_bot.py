# coding=utf-8
'''
Credits:
xiofan2[xiofan2/qq_retweet_bot]
anrio[Modifications/Suggestions]
'''

import requests
import tweepy
import json as js
import os
import sys
from urllib.parse import quote
import urllib.request
import json as js
import requests
import urllib
import random
import hashlib
import time
import datetime
from datetime import datetime
from datetime import timedelta


#Enter your keys
consumer_key = ''
consumer_secret = ''
access_token = '-'
access_token_secret = ''
baidu_app_id = ''
baidu_id_key = ''
retweet_group = 'Inari'
addr = 'http://127.0.0.1:11451'
#Process keys
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

def get_session(qq=''):
    global body_session, session
    # Setup tunnel
    response = requests.get(addr + '/about')
    rt1=str(response.text)
    ver = rt1[-9:-3]
    print('[Console] Mirai-Api-HTTP Version: ' + ver)
    body = '{"authKey":""}'
    response2 = requests.post(url=addr + '/auth', data=body)
    print('[Console] HTTP Status Code: ' + str(response2.status_code))
    # Gather session
    r2t = response2.text
    if r2t[8] == '0':
        session = r2t[21:-2]
        print('[Console] Session Code: ' + str(session))
    else:
        print(r2t[8])
    # Verify session
    body_session = '{"sessionKey":"' + session + '","qq":"' + qq + '"}'
    response3 = requests.post(url=addr + '/verify', data=body_session)
    r3t = response3.text
    if r3t[8] == '0':
        print('[Console] [get_session] Successfully connected to Mirai-Api-HTTP server!\n')
    else:
        print('[Console] [get_session] Failed!')
        print(r3t)
    return session


def release_session():
#Session keys need to be released immediately everytime you finish the process
    response = requests.post(url=addr + '/release', data=body_session)
    rt = response.text
    if rt[8] == '0':
        print('[Console] [release_session] Successfully Released Session ID!')
    else:
        print('[Console] [release_session] Failed!')
    return 0


def send_group_mirai(datatobesent, qq_group_id):
    body_tobesent = '{"sessionKey":"' + session + '","target": ' + str(
        qq_group_id) + ''',"messageChain":[{"type": "Plain", "text":"''' + datatobesent + '"}]}'
    response4 = requests.post(url=addr + '/sendGroupMessage', data=body_tobesent.encode('utf-8'))
    r4t = response4.text
    print(r4t.replace('{"code":','[Console] [send_group_mirai] Code: ').replace(',"msg":'," | Message: ").replace(',"messageId":',' | Message ID: ').replace('}',''))
    return 0


def analysis_time(retweet_time):
    offset_hours = 8
    local_timestamp = retweet_time + timedelta(hours=offset_hours)
    final_timestamp = datetime.strftime(local_timestamp, '%m.%d %H:%M:%S')
    return final_timestamp


def send_qqgroup_message(retweet_time, tweet_data, actual_name, qq_group_id, reply_user_name, reply_text, rt_tweet_text,
                         rt_user, repeat):
    # str(retweet_time,actual_name)
    message_format = '🌸' + actual_name + '🌸 于' + retweet_time + '更新了推文🍀\n\n'
    original_tweet_data = tweet_data
    if repeat == '0':
        original_tweet_data = tweet_data + '\n----\n' + tweet_data
    elif repeat == '1':
        original_tweet_data = tweet_data
    if reply_user_name != 'NULL':
        tweet_data = message_format + original_tweet_data + '\n\n回复 🌴' + reply_user_name + '🌴\n\n' + reply_text
        translate_tweet_data = translate(original_tweet_data.replace('\n','🍄').replace('「','🍺').replace('」','🍉'))
        translate_reply = translate(reply_text.replace('\n','🍄').replace('「','🍺').replace('」','🍉'))
        translate_data = '由 🍧百度翻译🍧 提供的翻译：\n\n' + translate_tweet_data + '\n\n回复 🌴' + reply_user_name + '🌴\n\n' + translate_reply
    elif rt_user != '':
        tweet_data = message_format + original_tweet_data + '\n\n转发 🍁' + rt_user + '🍁\n\n' + rt_tweet_text
        translate_tweet_data = translate(original_tweet_data.replace('\n','🍄').replace('「','🍺').replace('」','🍉'))
        translate_rt_text = translate(rt_tweet_text.replace('\n','🍄').replace('「','🍺').replace('」','🍉'))
        translate_data = '由 🍧百度翻译🍧 提供的翻译：\n\n' + translate_tweet_data + '\n\n转发 🍁' + rt_user + '🍁\n\n' + translate_rt_text
    else:
        tweet_data = message_format + original_tweet_data
        translate_tweet_data = translate(original_tweet_data.replace('\n','🍄').replace('🍺','「').replace('🍉','」'))
        translate_data = '由 🍧百度翻译🍧 提供的翻译：\n\n' + translate_tweet_data
    #	tweet_data=tweet_data.encode('utf-8')
    print('\n\nFound new tweet!'+'\n'+tweet_data)
    #	urllib.request.urlopen('http://127.0.0.1:5700/send_group_msg?group_id='+ str(qq_group_id) + '&message='+ tweet_data)
    send_group_mirai(tweet_data, qq_group_id)
    send_group_mirai(translate_data.replace('🍄','\n'), qq_group_id)
    return


def send_picture(qq_group_id, url):
    #	url=quote("[CQ:image,file="+url+"]")
    #	urllib.request.urlopen('http://127.0.0.1:5700/send_group_msg?group_id='+ str(qq_group_id) + '&message='+ url)
    image_tobesent = '{"sessionKey":"' + session + '","group": ' + str(qq_group_id) + ''',"urls":["''' + url + '"]}'
    response5 = requests.post(url=addr + '/sendImageMessage', data=image_tobesent)
    r5t = response5.text
    print('[Console] [send_picture] Successfully sent image, ImageID: '+ r5t[2:-2])
    return


def recog_tag(tags_data, match_tag):
    for single_tag in tags_data:
        for single_match_tag in match_tag:
            if single_match_tag == single_tag['text']:
                tags = 0
            else:
                tags = 1
    return tags


def analysis_screen_name(screen_name):
    user = api.get_user(screen_name)
    name = user.name
    return name


def readfile(txtname):
    last_id = 0
    if not os.path.exists(txtname):
        fileread = open(txtname, "a+")
        fileread.close()
    else:
        fileread = open(txtname, "r")
        for i in fileread.readlines():
            print('[Console] [readfile] Processed: '+i)
            if i is not '':
                last_id = int(i)
            fileread.close()
    return last_id


def writefile(txtname, last_id):
    filewrite = open(txtname, "w+")
    filewrite.writelines(str(last_id))
    filewrite.close()


def get_in_reply_tweet(in_reply_id):
    status = api.get_status(in_reply_id, tweet_mode='extended')
    return status.full_text


def send_tweet(new_tweets, actual_name, qq_group_id, tags, reply_user_name, last_id, match_tag, repeat, with_picture):
    tags = 0
    for status in reversed(new_tweets):
        try:
            media = status.extended_entities.get('media', [])
        except:
            media = ''
        try:
            tags_data = status.entities.get('hashtags', [])
            tags = recog_tag(tags_data, match_tag)
        except:
            tags = 1
        try:
            reply_user_screen_name = status.in_reply_to_screen_name
            reply_user_name = analysis_screen_name(reply_user_screen_name)
        except:
            reply_user_name = 'NULL'
        try:
            tags_data = status.entities.get('hashtags', [])
            tags = recog_tag(tags_data, match_tag)
        except:
            tags = 1
        try:
            in_reply_id = status.in_reply_to_status_id
            reply_text = get_in_reply_tweet(in_reply_id)
        except:
            reply_text = ''

        try:
            rt_tweet_text = status.quoted_status.full_text
            rt_user = status.quoted_status.user.name

        except:
            rt_tweet_text = ''
            rt_user = ''

        retweet_text = status.full_text
        retweet_time = analysis_time(status.created_at)
        if last_id == 0:
            last_id = status.id
        elif status.id > last_id:
            last_id = status.id
        if tags == 0 or match_tag == 0:
            send_qqgroup_message(retweet_time, retweet_text, actual_name, qq_group_id, reply_user_name, reply_text,
                                 rt_tweet_text, rt_user, repeat)
            print('[Console] [send_tweet] Retweet successed!')
            mu = [m['media_url'] for m in media]
            for n in mu:
                if media != '' and with_picture == 1:
                    send_picture(qq_group_id, n)
                    print('[Console] [send_tweet] Send image successed! Image URL: ' + n)
    return last_id


def retweet(screen_name, actual_name, qq_group_id, match_tag, repeat, with_picture):
    # actual_name=actual_name.encode("utf-8").decode("latin1")
    txtname = retweet_group + '_' + screen_name + '_tweet_ids.txt'
    tags = 0
    reply_user_name = 'NULL'
    last_id = readfile(txtname)
    if last_id == 0:
        new_tweets = api.user_timeline(screen_name=screen_name, count=1, tweet_mode='extended', include_rts='false',
                                       include_entities=True)
        last_id = send_tweet(new_tweets, actual_name, qq_group_id, tags, reply_user_name, last_id, match_tag, repeat,
                             with_picture)
        writefile(txtname, last_id)
    else:
        new_tweets = api.user_timeline(screen_name=screen_name, since_id=last_id, include_rts='false',
                                       tweet_mode='extended', include_entities=True)
        last_id = send_tweet(new_tweets, actual_name, qq_group_id, tags, reply_user_name, last_id, match_tag, repeat,
                             with_picture)
        writefile(txtname, last_id)

def translate(orig_text):
    orig_lang = 'auto'
    target_lang = 'zh'
    salt = random.randint(32768, 65536)

    orig_sign = baidu_app_id + orig_text + str(salt) + baidu_id_key
#    print(orig_sign) #debug
    m = hashlib.new('md5')
    m.update(orig_sign.encode(encoding="utf-8"))
    msign = m.hexdigest() #得到原始签名的MD5值
    data = {
        "q": orig_text,   
        "from": "auto",
        "to": "zh",
        "appid": baidu_app_id,
        "salt": salt,
        "sign": msign
    }
    url = "http://api.fanyi.baidu.com/api/trans/vip/translate"

    r = requests.get(url, params=data)
    if r.status_code == 200:
        try:
            result = r.json()
            translate_result = result["trans_result"][0]["dst"]
            print('\nTranslate result: ' + '\n' + translate_result)
        except:
            try:
                shit = '''!@#$%^&*(_+=-\][\';/\.,?><:"{}|`~（）【】；‘。、『』「」〔〕》《：“”~·￥'''
                for i in shit:
                    translate_result = result["trans_result"][0]["dst"]
                    translate_result = translate_result.replace(i,'☕')
                    print('\nTranslate result: ' + '\n' + translate_result)
            except:
                translate_result = ''
                
    else:
        print('[Console] [translate] Translation Failed!')

    return translate_result


#main
print('Stage1:Preparation'.center(50,'-')+'\n')
get_session()

#Enter your configs here
# retweet('screen_name','twitter_user's_real_name',qq_group_id,['tag'] or 0(no tag recognization),0(repeat) or 1(not_repeat),0(with_picture) or 1(without_picture))
print('\n'+'Stage2:Retweet'.center(50,'-')+'\n')
# xapenny
retweet('xapenny2015', 'xapenny', 884169045, 0, 0, 1)
# iOS讨论
retweet('CStar_OW', 'CoolStar', 567435967, 0, 0, 1)
retweet('nsimayu', '新岛夕', 567435967, 0, 0, 1)
retweet('unc0verTeam', 'unc0ver Team', 567435967, 0, 0, 1)
retweet('checkra1n', 'checkra1n', 567435967, 0, 0, 1)
retweet('axi0mX','axi0mX',567435967,0,0,1)
retweet('CharizTeam','Chariz Repository',567435967,0,0,1)
retweet('keen_lab','KEENLAB',567435967,0,0,1)
retweet('GetSileo','Sileo',567435967,0,0,1)
retweet('packixrepo','Packix Repository',567435967,0,0,1)
retweet('Pwn20wnd','@Pwn20wnd',567435967,0,0,1)
retweet('CorelliumHQ','Corellium',567435967,0,0,1)
retweet('electra_team','Electra Team',567435967,0,0,1)
retweet('i41nbeer','Ian Beer',567435967,0,0,1)
retweet('coolbooter','CoolBooter',567435967,0,0,1)
retweet('tihmstar','tihmstar',567435967,0,0,1)
retweet('Apple','Apple',567435967,0,0,1)
retweet('qwertyoruiopz','qwertyoruiop',567435967,0,0,1)
retweet('tim_cook','Tim Cook',567435967,0,0,1)
retweet('PanguTeam','PanguTeam',567435967,0,0,1)
#Key社family
retweet('iktd13_', 'Na-Ga', 198582349, 0, 0, 1)
retweet('takeshitaaaa', '竹下智博', 198582349, 0, 0, 1)
retweet('kay_comment', '魁', 198582349, 0, 0, 1)
retweet('maeda_jun_lab', '麻枝准研究所', 198582349, 0, 0, 1)
retweet('kamisama_Ch_AB', '神様になった日&Charlotte&AB!公式', 198582349, 0, 0, 1)
retweet('jun_owakon', '麻枝 准', 198582349, 0, 0, 1)
retweet('key_official', 'Key開発室', 198582349, 0, 0, 1)
retweet('kiyo_mizutsuki', '水月陵', 198582349, 0, 0, 1)
#聖翔音樂学院陕西分部
retweet('aibaaiai', '相羽あいな', 653076756, ['スタァライト'], 0, 1)
retweet('ayasa_ito', '伊藤 彩沙', 653076756, ['スタァライト'], 0, 1)
retweet('chichichi430', '生田 輝', 653076756, ['スタァライト'], 0, 1)
retweet('haruki_iwata', '岩田 陽葵', 653076756, ['スタァライト'], 0, 1)
retweet('k_moeka_', '小泉萌香', 653076756, ['スタァライト'], 0, 1)
retweet('koyamamomoyo', '小山 百代', 653076756, ['スタァライト'], 0, 1)
retweet('maho_tomita6261', '富田麻帆', 653076756, ['スタァライト'], 0, 1)
retweet('mimori_suzuko', '三森すずこ', 653076756, ['スタァライト'], 0, 1)
retweet('satohina1223', '佐藤日向', 653076756, ['スタァライト'], 0, 1)


print('\n\n'+'Stage3:Cleanup'.center(50,'-')+'\n')
release_session()
exit(0)
