# 说明:单文件版
import sys, os
import urllib.parse
import requests
import random
import hashlib
import json


# 读取文件
# 提取信息
# 调用接口
# 替换内容
# 生成文件

class bdt:
    appid = '20151113000005349'
    secretKey = 'osubCEzlGjzvw8qdQc41'
    myurl = '/api/trans/vip/translate'
    toLang = 'zh'
    langDict = {
        'zh_tw': 'cht',
    }

    def _bd_trans(self, q, lang=""):
        '''
        调用百度翻译接口进行翻译
        :param q: 多个单词以 \n 分隔，例：'watch\napple\nmaybe'
        :return: 例：{'watch': '看', 'apple': '苹果', 'maybe': '也许吧'}
        '''

        salt = random.randint(32768, 65536)

        lang = lang.lower()
        fromLang = 'auto'
        if lang and lang in self.langDict:
            fromLang = self.langDict[lang]

        sign = self.appid + q + str(salt) + self.secretKey
        m = hashlib.md5()
        m.update(sign.encode())
        sign = m.hexdigest()
        url = self.myurl + '?appid=' + self.appid + '&q=' + urllib.parse.quote(
            q) + '&from=' + fromLang + '&to=' + self.toLang + '&salt=' + str(salt) + '&sign=' + sign

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

    def bd_trans(self, datas, lang):
        '''
        自动整理 kv 并返回翻译
        :param datas:
        :return:
        '''
        res = {}
        tmp_str = ""
        for key in datas:
            if len(datas[key]) + len(tmp_str) > 1000:
                res.update(self._bd_trans(tmp_str, lang))
                tmp_str = ""
            tmp_str += datas[key] + "\n"

        res.update(self._bd_trans(tmp_str))

        return res


def parse(file_path):
    if not os.path.isfile(file_path):
        print("未找到文件！")
    with open(file_path) as f:
        datas = f.read()
    res = {}
    dres = {}
    lines = datas.split("\n")
    for line in lines:
        if not line: continue
        if 'a' < line[1].lower() < 'z':
            ei = line.find('=')
            res[line[:ei]] = line[ei + 1:]
            dres[line[ei + 1:]] = line[:ei]

    fy = bdt().bd_trans(res, 'ot')
    new_data = datas
    for v in fy:
        new_data = new_data.replace(
            dres[v] + "=" + v,
            dres[v] + "=" + fy[v],
        )
    with open('zh_CN.lang', 'w', encoding='utf-8') as f:
        f.write(new_data)
    print("保存成功")


def _help():
    print("""
    正确的打开方式是：python trans.py 要翻译的lang文件地址
    例： python trans.py C:/en_US.lang
    """)
    sys.exit(0)


def run():
    if len(sys.argv) != 2:
        _help()
    print(sys.argv)
    parse(sys.argv[1])


if __name__ == "__main__":
    run()
