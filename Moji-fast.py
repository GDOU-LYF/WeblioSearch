from ..base import *

import requests
import re
import json
import os

def wirte_word(worddict,word):#测试代码,写入
    fileword=json.dumps(worddict)
    _file="E:\\object\\weblio\\json\\Moji_{word}.json".format(word=word)
    fileObject = open(_file, 'w')
    fileObject.write(fileword)
    fileObject.close()

@register([u'Moji', u'Moji'])#接口名称
class Moji(WebService):#接口名称
    target_search = 'https://api.mojidict.com/parse/functions/search_v3' #查询单词ID
    target_fetch = 'https://api.mojidict.com/parse/functions/fetchWord_v2'#查询单词详细内容
    target_tts = 'https://api.mojidict.com/parse/functions/fetchTts_v2'#TTS

    hd = {'content-type': 'text/plain',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19551'}
    data={#单词列表
        'searchText':"",
        "needWords": True,
        "langEnv": "zh-CN_ja",
        "_SessionToken": "r:610f6ba0d8d2721e773a2b185b85590b",
        "_ApplicationId": "E62VyFVLMiW7kvbtVq3p",
        "_InstallationId": "5562c88b-b67a-c285-b9d1-a8360121380a",
        "_ClientVersion": "js2.12.0",
    }

    word_data={#单词详细数据
        "wordId": '', 
        "_SessionToken": "r:610f6ba0d8d2721e773a2b185b85590b", 
        "_ApplicationId": "E62VyFVLMiW7kvbtVq3p", 
        "_InstallationId": "5562c88b-b67a-c285-b9d1-a8360121380a", 
        "_ClientVersion": "js2.12.0",
    }

    word_tts={#这个是例句的
        "tarId":"",
        "tarType":103,
        "_SessionToken":"r:610f6ba0d8d2721e773a2b185b85590b",
        "_ApplicationId":"E62VyFVLMiW7kvbtVq3p",
        "_InstallationId":"5562c88b-b67a-c285-b9d1-a8360121380a",
        "_ClientVersion":"js2.12.0"
    }
    tts_data={#这个是单词的
        "tarId": '', 
        "tarType": 102, 
        "_SessionToken": "r:610f6ba0d8d2721e773a2b185b85590b", 
        "_ApplicationId": "E62VyFVLMiW7kvbtVq3p", 
        "_InstallationId": "5562c88b-b67a-c285-b9d1-a8360121380a", 
        "_ClientVersion": "js2.12.0"
    }
    def __init__(self):
        super(Moji, self).__init__()#接口名称
    def _get_from_api(self):
        self.data['searchText']=self.word
        r = requests.post(self.target_search, data=json.dumps(self.data), headers=self.hd)  # POST请求
        ans = r.json()['result']
        # wirte_word(ans,self.word)
        return self.cache_this(ans)
    @with_styles(cssfile="_moji.css", need_wrap_css=False,wrap_class='mojidict-helper-card-container')
    def _css(self, val):
        # 如果是 css="@import 'moji.css'"
        # # if os.path.exists('moji.css')==False:
        # #     from aqt.winpaths import get_appdata
        #     css_path=os.path.join(get_appdata(), "Anki2","addons21",'1807206748','service','static','_moji.css')#获取Anki的Fast插件位置
        #     import shutil
        #     try:
        #         shutil.copy(css_path,'_moji.css')
        #     except:
        #         pass
        return val
    @export('单词释义[简]')
    def mean_simple(self):
        words=self._get_field('words')
        ret='''<div class="mojidict-helper-card"><div class="word-detail-container">'''
        for word in words:
            if word['spell']==self.word or word['pron']==self.word:
                word_Part_of_speech='['+''.join(re.findall(r'\[(.*?)\]',word['excerpt']))+']<br>'#词性
                word_val=re.sub(r"\[(.*?)\]", "",word['excerpt']).split()#分割
                word_text=''
                for text in word_val:
                    word_text+=text+'<br>'
                word_text.rstrip('<br>')#去除末尾换行符
                word_text= word_Part_of_speech+word_text #词性+释义
                w='''<div class="word-detail"><span class="detail-title">{pron}</span><p>{excerpt}</p></div>'''.format(pron=word['pron'],excerpt=word_text)
                # w=u'{pron}:<br>{excerpt}<br>'.format(pron=word['pron'],excerpt=word['excerpt'])
                ret+=w
        ret=ret+'</div></div>'
        return self._css(ret)
        # return ret
    @export('单词发音')
    def mean_audio(self):
        words=self._get_field('words')
        self.tts_data['tarId']=words[0]['objectId']
        r_tts = requests.post(self.target_tts, data=json.dumps(self.tts_data), headers=self.hd)#取单词发音
        tts_url=r_tts.json()['result']['result']['url']
        audio_name = get_hex_name(self.unique.lower(), re.search(r'.*?(?=&Expires)',tts_url[tts_url.rindex('/') + 1:]).group(), 'mp3')#唯一标识
        if os.path.exists(audio_name) or self.download(tts_url, audio_name, 5):
            with open(audio_name, 'rb') as f:
                if f.read().strip() == '{"error":"Document not found"}':
                    res = ''
                else:
                    res = self.get_anki_label(audio_name, 'audio')
            if not res:
                os.remove(audio_name)
        return res