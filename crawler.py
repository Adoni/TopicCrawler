#!/usr/bin/env python
#coding=utf8
import pika
import urllib2
from helper import sleep
import cookielib
from helper import get_target
import sys
import random
import time
import copy

#from contentEncodingProcessor import ContentEncodingProcessor
import socket

global cookieJar
global sleep_time
global headers
global url_opener

def install_cookie(cookie_file_name):
    global cookieJar
    cookieJar = cookielib.LWPCookieJar(cookie_file_name)
    cookieJar.load( ignore_discard=True, ignore_expires=True)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar));
    urllib2.install_opener(opener);
    print('Install Cookie Done')

def get_request(body):
    if('timestamp' in body['url']):
        url=body['url'].replace('timestamp', str(int(time.time()*1000)))
    else:
        url=body['url']
    headers=body['headers']
    print url
    print headers
    request=urllib2.Request(
            url=url,
            headers=headers)
    return request

def get_html(body):
    global sleep_time
    request=get_request(body)
    print 'getting'
    try:
        #response=url_opener.open(request)
        response=urllib2.urlopen(request,timeout=30)
        print response.info()
        html=response.read()
        print 'done'
    except Exception as e:
        print e
        print e.info()
        print e.read()
        print('Retry')
        sleep(10)
        request=get_request(body)
        try:
            response=urllib2.urlopen(request,timeout=30)
            html=response.read()
            #html=url_opener.open(request).read()
        except Exception as e:
            print e
            print e.info()
            print e.read()
            print('Retry')
            print 'get html error'
            return ''
    if('location.replace' in html):
        print('Redirect..')
        print('Try to get target')
        target=get_target(html)
        open('./keke.html','w').write(html)
        print target
        if(target==None):
            print(body)
            print 'get target error'
            print(html)
            return ''
        else:
            body['url']=target[0]
            html=get_html(body)
            #cookieJar.save()
            return html
    else:
        return html

#定义接收到消息的处理方法
def request(ch, method, properties, body):
    #print " [.] increase(%s)"  % (body,)
    body=eval(body)
    response = get_html(body)
    print '==============   Html Begin  ====================='
    print response
    print '==============   Html End  ====================='
    #将计算结果发送回控制中心
    ch.basic_publish(exchange='',
                     routing_key=properties.reply_to,
                     body=response)
    if(body['need_sleep']):
        sleep(sleep_time)
    ch.basic_ack(delivery_tag = method.delivery_tag)
    print '=========   Complete Crawl   ========='


def install_proxy(proxy):
    print proxy
    opener = urllib2.build_opener(urllib2.ProxyHandler({'http':proxy}), urllib2.HTTPHandler(debuglevel=1))
    urllib2.install_opener(opener)
    print('Install Proxy Done')

if __name__ == '__main__':
    #连接rabbitmq服务器
    cookie_file_name='./cookies/cookie_'+str(sys.argv[1])
    install_cookie(cookie_file_name)
    #安装代理
    proxies=open('./proxies.seed').readlines()
    index=random.randint(0,len(proxies)-1)
    proxy=proxies[index].replace('\n','').replace('\r','')
    #install_proxy(proxy)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost'))
    channel = connection.channel()
    sleep_time=50
    #encoding_support = ContentEncodingProcessor
    #url_opener = urllib2.build_opener( encoding_support, urllib2.HTTPHandler )
    #定义队列
    channel.queue_declare(queue='topic')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(request, queue='topic')
    channel.start_consuming()
