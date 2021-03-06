# /usr/bin/env python
import urllib.parse
import requests
import random
import hashlib
import json

appid = '20151113000005349'
secretKey = 'osubCEzlGjzvw8qdQc41'
myurl = '/api/trans/vip/translate'
toLang = 'zh'
langDict = {
    'zh_tw': 'cht',
}


def _bd_trans(q, lang=""):
    '''
    调用百度翻译接口进行翻译
    :param q: 多个单词以 \n 分隔，例：'watch\napple\nmaybe'
    :return: 例：{'watch': '看', 'apple': '苹果', 'maybe': '也许吧'}
    '''

    salt = random.randint(32768, 65536)

    lang = lang.lower()
    fromLang = 'auto'
    if lang and lang in langDict:
        fromLang = langDict[lang]

    sign = appid + q + str(salt) + secretKey
    m = hashlib.md5()
    m.update(sign.encode())
    sign = m.hexdigest()
    url = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(
        q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(salt) + '&sign=' + sign

    res = {}

    reqs = requests.get('http://api.fanyi.baidu.com' + url)
    if reqs.status_code != 200:
        print("调用百度翻译接口失败")
        print(reqs._content)
        return 'err'
    datas = json.loads(reqs._content.decode())
    for data in datas['trans_result']:
        res[data['src']] = data['dst']

    return res




def bd_trans(datas, lang):
    '''
    自动整理 kv 并返回翻译
    :param datas:
    :return:
    '''
    res = {}
    tmp_str = ""
    for key in datas:
        if len(datas[key]) + len(tmp_str) > 1000:
            res.update(_bd_trans(tmp_str, lang))
            tmp_str = ""
        tmp_str += datas[key] + "\n"

    res.update(_bd_trans(tmp_str))

    return res


if __name__ == "__main__":
    print(_bd_trans('watch\napple\nmaybe'))
