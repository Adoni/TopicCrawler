#coding:utf8
#from loginModule import LoginModule
import re
import os
import json
import time
import re
import random
import urllib2
import cookielib
import hashlib
import gzip

from helper import get_pages
from helper import get_target
from helper import get_topics
from helper import get_huatis
from helper import md5
from helper import get_category_location_tag
from helper import get_counts
from helper import get_description
from helper import get_emcee

from deliver import Deliver
from crawler import get_html


class TopicSpider():
    sleep_time=50
    access_token = '2.00L9khmFlxpd6C91aec9ef010s3KCc'
    MAX_USER_COUNT=200
    MAX_TOPIC_COUNT=100
    MAX_PAGE_COUNT=1000

    all_headers = {
            'simple_headers':{'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'},
            'huati_headers':{
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                #'Accept-Encoding':'gzip,deflate,sdch',
                'Accept-Language':'zh-CN,zh;q=0.8',
                'Cache-Control':'max-age=0',
                'Connection':'keep-alive',
                #'Host':'www.weibo.com',
                'User-Agent':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36'
                },
            'user_huati_headers':{}
            }

    def __init__(self):
        self.time_stamp=time.time()
        print('BaseSpider')
        self.deliver=Deliver()

    def get_html(self, url, headers, need_sleep=True):
        body={
                'url':url,
                'headers':headers,
                'need_sleep':need_sleep
                }
        html=self.deliver.request(body)
        return html

    def get_uids_and_comments(self, topic):
        total=200
        count=50
        uids=[]
        comments=[]
        for i in range(0,total/count):
            base_url='https://api.weibo.com/2/search/topics.json?'
            complete_url=base_url+'access_token='+self.access_token+'&q='+urllib2.quote(topic)+'&count='+str(count)+'&page='+str(i+1)
            html=self.get_html(complete_url, False)
            if(html=='' or 'error' in html):
                print('get html error')
                print(complete_url)
                return uids, comments
            try:
                json_data=json.loads(html)
            except:
                print('load html error')
                return uids, comments
            for status in json_data['statuses']:
                uids.append(status['user']['idstr'])
                comment=[]
                comment.append(str(status['mid']))
                comment.append(status['text'])
                comment.append(status['created_at'])
                comment.append(status['source'])
                comment.append(status['user']['idstr'])
                comment.append(status['user']['province'])
                comment.append(status['user']['city'])
                comment.append(status['user']['location'])
                comment.append(status['user']['gender'])
                comment.append(str(status['user']['followers_count']))
                comment.append(str(status['user']['friends_count']))
                comment.append(str(status['user']['bi_followers_count']))
                comment.append(str(status['user']['verified']))
                comments.append('\t'.join(comment))
        return list(set(uids)), comments

    def output_keke(self, html):
        open('./keke.html','w').write(html)

    def get_huatis(self, uid):
        base_url='http://huati.weibo.com/aj_profile/show?uid='+str(uid)+'&pagesize=20&p='

        page_count=1
        huatis=[]
        while(True):
            print('\t-Getting page '+str(page_count)+' pages of user '+str(uid))
            str_time='&_t=0&__rnd='+'timestamp'
            complete_url=base_url+str(page_count)+str_time
            print(complete_url)
            html=self.get_html(complete_url,self.all_headers['simple_headers'])
            open('keke.html','w').write(html)
            html=gzip.GzipFile(mode="rb", fileobj=open('./keke.html', 'rb')).read()
            try:
                json_data=json.loads(html)
            except:
                print('Sorry, load json error')
                print(html)
                return huatis
            if(u'data' in json_data and u'html' in json_data[u'data']):
                html=json_data[u'data'][u'html']
            else:
                print('no')
                print(html)
                break
            if(html==''):
                print('Enough')
                break
            print('=================================')
            tmp_huatis=get_huatis(html)
            if(tmp_huatis==[]):
                break
            for huati in tmp_huatis:
                if(huati in huatis):
                    print('wa')
                    return huatis
                huatis.append(huati)
            page_count+=1
        return huatis

    def get_topics(self, uid):
        base_url='http://weibo.com/p/100206'
        suffix='/topic?from=page_100505&mod=TAB#place'
        complete_url=base_url+str(uid)+suffix
        html=self.get_html(complete_url)
        if(html==''):
            print('Error in get html!')
            print(complete_url)
            return None

        pages=get_pages(html)
        if(pages==None):
            topics=get_topics(html)
            if(not topics==[]):
                print(complete_url)
                return list(set(topics))
            else:
                print('Cannot get pages')
                print(complete_url)
                return None

        topics=[]
        for page in pages:#[0:self.MAX_PAGE_COUNT]:
            print('\t-Getting page '+str(pages.index(page))+'\\'+str(len(pages))+' of user '+str(uid))
            page='http://weibo.com'+page
            html=self.get_html(page)
            if(html==''):
                print(page)
                print('Error')
                continue
            for topic in get_topics(html):
                topics.append(topic)
        return list(set(topics))

    def get_topic_information(self, topic):
        base_url='http://weibo.com/p/100808'
        topic=topic.replace('#','')
        topic=topic.replace('\r','')
        topic=topic.replace('\t','')
        complete_url=base_url+md5(topic)#+'?k='+topic
        print('Now get html for topic information')
        html=self.get_html(complete_url, self.all_headers['huati_headers'])
        print('Got html for topic information')
        if html=='':
            print('Error when getting topic information')
            print(complete_url)
            return None
        information=dict()
        information['topic_name']=topic.replace('#','').decode('utf8')

        counts=get_counts(html)
        print counts
        if(counts==None):
            self.output_keke(html)
            return None
        information['readers_count']=counts[0]
        information['discuss_count']=counts[1]
        information['followers_count']=counts[2]

        attributes=get_category_location_tag(html)
        print attributes
        if(attributes==None):
            self.output_keke(html)
            return None
        information['category']=';'.join(attributes[0])
        information['location']=';'.join(attributes[1])
        information['tags']=';'.join(attributes[2])
        emcee=get_emcee(html)
        print emcee
        if(emcee==None):
            self.output_keke(html)
            return None
        information['host']=emcee
        description=get_description(html)
        print description
        if(description==None):
            self.output_keke(html)
            return None
        information['description']=description
        print 'Success to get topic information'
        return information

    def get_user_information(self, key_type, key):
        base_url='https://api.weibo.com/2/users/show.json?'
        complete_url=base_url+'access_token='+self.access_token+'&'+str(key_type)+'='+key
        html=self.get_html(complete_url, self.all_headers['simple_headers'], False)
        if(html=='' or 'error' in html):
            print('error')
            print(complete_url)
            print key
            return None
        html=html
        json_data=json.loads(html)
        information=dict()
        information['uid']=str(json_data['id'])
        information['province']=str(json_data['province'])
        information['city']=str(json_data['city'])
        information['location']=json_data['location']
        information['gender']=str(json_data['gender'])
        information['followers_count']=str(json_data['followers_count'])
        information['friends_count']=str(json_data['friends_count'])
        information['bi_followers_count']=str(json_data['bi_followers_count'])
        information['verified']=str(json_data['verified'])
        return information

    def output_topic_comments(self, topic, comments):
        print 'Output '+topic
        try:
            file_out=open('./data/topic/'+topic.replace('#','').replace('\r','')+'.data','a')
        except:
            return
        for comment in comments:
            file_out.write(comment.encode('utf8')+'\n')
        file_out.close()
        return

    def output_topic_information(self, information):
        file_out=open('./data/topic/topics.data','a')
        keys=['topic_name',
                'description',
                'category',
                'location',
                'tags',
                'readers_count',
                'discuss_count',
                'followers_count']
        line=[]
        for key in keys:
            if information[key]==None:
                line.append('Null')
            else:
                try:
                    line.append(information[key].decode('utf8'))
                except:
                    line.append(information[key])
        print line
        line='\t'.join(line)+'\n'
        file_out.write(line.encode('utf8'))
        file_out.close()
        return

    def output_topic_host_information(self, information):
        file_out=open('./data/topic/hosts.data','a')
        keys=['topic_name',
                'uid',
                'province',
                'city',
                'location',
                'gender',
                'followers_count',
                'friends_count',
                'bi_followers_count',
                'verified']
        line=[]
        for key in keys:
            line.append(information[key])
        line='\t'.join(line)+'\n'
        file_out.write(line.encode('utf8'))
        file_out.close()
        return

    def output_user_information(self, information):
        file_out=open('./data/user/users.data','a')
        keys=['uid',
                'province',
                'city',
                'location',
                'gender',
                'followers_count',
                'friends_count',
                'bi_followers_count',
                'verified']
        line=[]
        for key in keys:
            line.append(information[key])
        line='\t'.join(line)+'\n'
        file_out.write(line.encode('utf8'))
        file_out.close()
        return

    def output_user_topics(self, uid, topics):
        file_out=open('./data/user/'+str(uid)+'.data','a')
        for topic in topics:
            line=str(uid)+'\t'+topic.replace('#','').replace('\r','')+'\n'
            file_out.write(line.encode('utf8'))
        return

    def output_user_participation(self, participation):
        file_out=open('./data/user/partition.data','w')
        print(participation)
        for uid in participation:
            file_out.write(uid+'\t'+str(participation[uid])+'\n')

    def output_tmp_uids(self, uids):
        file_out=open('./data/tmp/uids.data','w')
        for uid in uids:
            file_out.write(str(uid)+'\n')

    def output_tmp_topics(self, uid, topics):
        file_out=open('./data/tmp/user_topics.data','a')
        file_out.write(str(uid))
        for topic in topics:
            file_out.write('\t'+topic.encode('utf8'))
        file_out.write('\n')

    def get_get_topics(self, uid):
        base_url='http://huati.weibo.com/profile/'
        complete_url=base_url+str(uid)
        html=self.get_html(complete_url)
        if(html==''):
            print('Error in get html!')
            print(complete_url)
            base_url='http://weibo.com/p/100505'
            suffix='/topic?from=page_100505&mod=TAB#place'
            complete_url=base_url+str(uid)+suffix
            print(' Let\'s we try '+complete_url)
            html=self.get_html(complete_url)
            if(html==''):
                print('Shiiiiiit')
                return None

        topics=get_topics(html)
        return topics

    def update_topics(self, topics):
        file_out=open('./candidates.seed','w')
        for topic in topics:
            topic=topic[0]+'\n'
            file_out.write(topic)
        file_out.close()

    def get_existed_topics(self):
        try:
            filenames=os.listdir('./data/topic/')
            for name in filenames:
                filenames[filenames.index(name)]='#'+name[:-5]+'#'
            return filenames
        except:
            return []

    def get_existed_topic_information(self):
        try:
            f=open('./data/topic/topics.data')
            topics=[]
            for line in f:
                topic=line.replace('\n','').split('\t')[0]
                topics.append('#'+topic+'#')
            return topics
        except:
            return []

    def restart_crawl_user_topics(self):
        print 'Try to restart'
        uids=[]
        to_crawl_uids=[]
        #载入uids
        for uid in open('./data/tmp/uids.data'):
            uids.append(uid.replace('\n',''))
            to_crawl_uids.append(uid.replace('\n',''))
        user_topics=dict()
        #载入to_crawl_uids和user_topics
        try:
            #移除已经爬到的
            for line in open('./data/tmp/user_topics.data'):
                line=line.replace('\n','')
                line=line.split('\t')
                if(len(line)==0):
                    continue
                uid=line[0]
                if(uid in to_crawl_uids):
                    to_crawl_uids.remove(uid)
                user_topics[uid]=line[1:]
            #移除已经失败的
            for line in open('./data/user/fail_users.data'):
                line=line.replace('\n','')
                if(line==''):
                    continue
                uid=line
                if(uid in to_crawl_uids):
                    to_crawl_uids.remove(uid)
        except:
            print 'Got '+str(len(uids))+' uids'
            print 'Got '+str(len(user_topics))+' existing users'
        print 'Got '+str(len(uids))+' uids'
        print 'Got '+str(len(user_topics))+' existing users'

        #将所有用户再次去重
        uids=list(set(all_uids))
        to_crawl_uids=list(set(all_uids))
        self.output_tmp_uids(uids)
        user_topics=dict()

        #2.获取用户所参与的所有topic
        for uid in to_crawl_uids:
            #获取用户topics
            print('Getting '+str(uids.index(uid))+'\\'+str(len(uids))+' users')
            huatis=self.get_huatis(uid)
            topics=None
            if (huatis==None and topics==None):
                ff=open('./data/user/fail_users.data','a')
                ff.write(str(uid)+'\n')
                print('mark')
                continue
            if(huatis==None):
                topics=topics
            else:
                if(topics==None):
                    topics=huatis
                else:
                    if(len(huatis)>len(topics)):
                        topics=huatis
            if(len(topic)==0):
                ff=open('./data/user/fail_users.data','a')
                ff.write(str(uid)+'\n')
                print('mark')
                continue
            for topic in topics:
                print topic
            print('Get '+str(len(topics))+' topics')
            user_topics[uid]=topics
            self.output_tmp_topics(uid, topics)
            print('Success to get topics of user '+str(uid))

    def crawl_comments(self):
        all_uids=[]
        existed_topics=self.get_existed_topics()
        #1.获取每个topic的评论及去重之后的user列表
        for topic in candidate_topics:#[0:self.MAX_TOPIC_COUNT]:
            print('Getting '+str(candidate_topics.index(topic))+'\\'+str(len(candidate_topics))+' topics')
            if(topic in existed_topics):
                print topic+' is already crawled'
                continue
            uids, comments=self.get_uids_and_comments(topic)
            #输出话题评论
            self.output_topic_comments(topic, comments)
            print('Success to get uids of topic '+topic)
        #将所有用户再次去重
        uids=list(set(all_uids))
        to_crawl_uids=list(set(all_uids))
        self.output_tmp_uids(uids)
        user_topics=dict()

    def crawl_topic_information_and_host_information(self):
        #获取每个topic的information host
        candidate_topics=self.get_existed_topics()
        existed_topic_information=self.get_existed_topic_information()
        print existed_topic_information
        for topic in candidate_topics:
            #获取候选集中话题的信息
            if topic in existed_topic_information:
                print '%s is existed'%topic
                continue
            print topic
            topic_information=self.get_topic_information(topic)
            if(topic_information==None):
                print 'Topic information is None'
                print topic
                continue
            #获取话题主持人信息
            host_information=self.get_user_information('screen_name',topic_information['host'])
            if(host_information==None):
                print 'Host information is None'
                print topic
                print topic_information['host']
                print type(topic)
                print type(topic_information['host'])
                continue
            host_information['topic_name']=topic.replace('#','').replace('\r','').decode('utf8')
            self.output_topic_information(topic_information)
            self.output_topic_host_information(host_information)
            print('Success to get uids of topic '+topic)


    def iterate(self):
        #3.统计用户的参与度
        participation=dict()
        for uid in user_topics.keys():
            topics=user_topics[uid]
            part_count=0
            for topic in topics:
                topic=topic.encode('utf8')
                if topic in candidate_topics:
                    part_count+=1
            participation[uid]=part_count
        self.output_user_participation(participation)

        #4.根据参与度排序，取top200的用户
        users=sorted(participation.iteritems(), key=lambda d:d[1], reverse = True)[0:self.MAX_USER_COUNT]
        #5.统计每个话题的出现频度
        new_candidate_topics=dict()
        for uid in users:
            uid=uid[0]
            #获取用户信息
            user_information=self.get_user_information('uid', uid)
            if(user_information==None):
                continue
            topics=user_topics[uid]
            #输出用户信息和用户参与过的话题信息
            self.output_user_information(user_information)
            self.output_user_topics(uid, topics)
            for topic in topics:
                topic=topic.encode('utf8')
                if topic in candidate_topics:
                    continue
                if topic in new_candidate_topics:
                    new_candidate_topics[topic]+=1
                else:
                    new_candidate_topics[topic]=1
        #6.根据话题的出现频度排序，取top50
        topics=sorted(new_candidate_topics.iteritems(), key=lambda d:d[1], reverse = True)[0:self.MAX_TOPIC_COUNT]
        #7.更新话题种子信息
        self.update_topics(topics)
        print('Success to iterate')

    def start_requests(self):
        self.crawl_topic_information_and_host_information()

if(__name__=='__main__'):
    a=TopicSpider()
    a.start_requests()
    #topic_information=a.get_topic_information('#十年记忆，淘宝时光#')
    #host=a.get_user_information('screen_name',topic_information['host'])
    #print host
