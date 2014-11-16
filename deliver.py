#!/usr/bin/env python
#coding=utf8
import pika

class Deliver(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

        self.channel = self.connection.channel()
        #定义接收返回消息的队列
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response,
                                   no_ack=True,
                                   queue=self.callback_queue)

    #定义接收到返回消息的处理方法
    def on_response(self, ch, method, props, body):
        self.response = body


    def request(self, body):
        self.response = None
        #发送计算请求，并声明返回队列
        self.channel.basic_publish(exchange='',
                                   routing_key='topic',
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         ),
                                   body=str(body))
        #接收返回的数据
        while self.response is None:
            self.connection.process_data_events()
        return self.response
