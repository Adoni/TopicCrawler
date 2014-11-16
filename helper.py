#coding:utf8
import re
import hashlib
import types
from lxml import etree
import time
import random

def get_last_uid(fname):
    f=open(fname).readlines()
    last_uid=f[-1].split('\t')[0]
    return last_uid

def get_new_line_num(fname1, fname2):
    try:
        open(fname1)
    except:
        return 0
    last_uid=get_last_uid(fname1)
    return open(fname2).readlines().index(last_uid+'\n')

def get_href_from_text(html, text):
    pat='<a[^<,>]*>'+text+'<'
    with_hrefs=re.findall(pat,html)
    ans=[]
    for with_href in with_hrefs:
        with_href=with_href.replace('\\','')
        pat='href="[^"]*"'
        href=re.search(pat,with_href)
        if(href==None):
            return None
        else:
            ans.append(href.group()[6:-1])
    if(ans==[]):
        return None
    return ans

def md5(s):
    if type(s) is types.StringType:
        m = hashlib.md5()
        m.update(s)
        return str(m.hexdigest())
    else:
        return ''

def get_htmls_by_domid(html, domid):
    pat=ur'{.*"domid":"%s.*}'%domid
    try:
        results=re.findall(pat, html.decode('utf8'))
    except:
        results=re.findall(pat, html)
    if(results==[]):
        print 'No html'
        return None
    try:
        htmls=[]
        for result in results:
            if 'html' in result:
                html=normal(result[result.index('html')+7:-2])
                #htmls.append(normal(result['html']).decode('utf8'))#[22:-1].replace('\\','')
                htmls.append(html)
        return htmls
    except Exception as e:
        print e
        print 'No dict'
        return None

def get_school(html):
    if(not '&school' in html):
        return None
    pat='<a[^<>]*&school[^<>]*>[^<>]*<'
    a=re.findall(pat,html)
    ans=[]
    for school in a:
        pat='>.*<'
        school=re.findall(pat,school)
        if(school==[]):
            continue
        else:
            ans.append(school[0][1:-1])
    if(ans==[]):
        return None
    else:
        return ans

def get_target(html):
    if(not 'location.replace' in html):
        print('No location.replace in html')
        return None
    pat="location.replace\('[^']*'\)"
    a=re.findall(pat,html)
    pat='location.replace\("[^"]*"\)'
    b=re.findall(pat,html)
    ans=[]
    for url in a:
        ans.append(url[18:-2])
    for url in b:
        ans.append(url[18:-2])
    if(ans==[]):
        return None
    else:
        return ans

def get_topics(html):
    pat=ur"#[\u4e00-\uffff,A-Z,a-z,0-9]+#"
    try:
        topics=re.findall(pat,html.decode('utf8'))
    except:
        topics=re.findall(pat,html)
    return topics

def get_huatis(html):
    html=normal(html)
    tree = etree.HTML(html)
    nodes = tree.xpath(u'//div[@class="list_pictext_bg"]//dd[@class="title"]//a')
    huatis=[]
    for node in nodes:
        huatis.append(node.text)
    return huatis

def get_pids(html):
    pat=u'Pl_Core_LeftPicTextMixedGalley__[0-9]+'
    pids=re.findall(pat, html.decode('utf8'))
    if(pids==[]):
        return None
    else:
        return pids[0]

def get_pages(html):
    text='第&nbsp;[0-9]+&nbsp;页'
    return get_href_from_text(html, text)

def remove_trn(s):
    strings=['\t','\r','\n']
    for ss in strings:
        s=s.replace(ss,'')
    return s
def get_description(html):
    domid='Pl_Third_Inline__'
    htmls=get_htmls_by_domid(html, domid)
    if htmls==None:
        print 'No description'
        return None
    for html in htmls:
        if not u'导语' in html:
            continue
        tree=etree.HTML(html)
        result=tree.xpath('string()')
        return remove_trn(normal(result)).replace(' ','').encode('utf8')
    return None

def get_emcee(html):
    domid='Pl_Core_Ut2UserList__'
    htmls=get_htmls_by_domid(html, domid)
    if htmls==None:
        print 'No host'
        return None
    for html in htmls:
        if not u'话题主持人' in html:
            continue
        tree=etree.HTML(html)
        nodes=tree.xpath(u'//a[@class="S_txt1"]')
        result=None
        for node in nodes:
            result=node.get('title').encode('utf8')
        return result
    return None

def normal(html):
    to_replace=dict()
    to_replace['\\t']='\t'
    to_replace['\\n']='\n'
    to_replace['\\r']='\r'
    to_replace['\\"']='"'
    to_replace['\\/']='/'
    for key in to_replace.keys():
        html=html.replace(key, to_replace[key])
    return html

def get_category(html):
    domid='Pl_Core_T5MultiText__'
    htmls=get_htmls_by_domid(html, domid)
    if htmls==None:
        return ['None']
    for html in htmls:
        if not u'分类：' in html:
            continue
        tree=etree.HTML(html)
        nodes=tree.xpath(u'//ul[@class="ul_auto clearfix"]/li[1]//a')
        words=[]
        for node in nodes:
            text=node.xpath('string()')
            text=remove_trn(text).replace(' ','')
            words.append(text.encode('utf8'))
        return words
    return ['None']

def get_location(html):
    domid='Pl_Core_T5MultiText__'
    htmls=get_htmls_by_domid(html, domid)
    if htmls==None:
        return ['None']
    for html in htmls:
        if not u'地区：' in html:
            continue
        tree=etree.HTML(html)
        nodes=tree.xpath(u'//ul[@class="ul_auto clearfix"]/li[1]//a')
        words=[]
        for node in nodes:
            text=node.xpath('string()')
            text=remove_trn(text).replace(' ','')
            words.append(text.encode('utf8'))
        return words
    return ['None']

def get_tag(html):
    domid='Pl_Core_T5MultiText__'
    htmls=get_htmls_by_domid(html, domid)
    if htmls==None:
        print 'No tags'
        return ['None']
    for html in htmls:
        if not u'标签：' in html:
            continue
        tree=etree.HTML(html)
        nodes=tree.xpath(u'//ul[@class="ul_auto clearfix"]/li[1]//a')
        words=[]
        for node in nodes:
            text=node.xpath('string()')
            text=remove_trn(text).replace(' ','')
            words.append(text.encode('utf8'))
        return words
    return ['None']

def get_category_location_tag(html):
    return get_category(html),get_location(html), get_tag(html)

def get_counts(html):
    domid='Pl_Core_T8CustomTriColumn__'
    htmls=get_htmls_by_domid(html,domid)
    if htmls==None:
        return None
    for html in htmls:
        if not u'阅读' in html:
            continue
        tree=etree.HTML(html)
        nodes=tree.xpath(u'//td[@class="S_line1"]//strong')
        words=[]
        for node in nodes:
            if('\t' in node.text or ' ' in node.text):
                continue
            words.append(node.text.encode('utf8'))
        if(len(words)<3):
            return None
        readers_count=words[0]
        discuss_count=words[1]
        followers_count=words[2]
        return readers_count, discuss_count, followers_count
    return None

def sleep(sleep_time):
    sleep_time=sleep_time+random.randint(-5,5)
    print('Sleeping for '+str(sleep_time)+' seconds')
    time.sleep(sleep_time)
    print('Wake up')

if __name__=='__main__':
    html=''.join(open('./keke.html').readlines())
    print get_counts(html)
    print get_description(html)
    print get_emcee(html)
    print get_category_location_tag(html)
