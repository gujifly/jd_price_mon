#!/usr/bin/env python
# encoding: utf-8

import urllib,urllib2
import json
import os,codecs
import logging,sys
from logging.handlers import RotatingFileHandler
import multiprocessing
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial

######################## 设置 logger ###############################
logger = logging.getLogger()
logger.setLevel(logging.INFO) # Log等级总开关
#定义一个RotatingFileHandler，最多备份5个日志文件，每个日志文件最大10M
Rthandler = RotatingFileHandler('%s.log'%(sys.argv[0]), maxBytes=10*1024*1024,backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
Rthandler.setFormatter(formatter)
logger.addHandler(Rthandler)
#----------------------------- logger end --------------------------#

mail_server='mail-provider_ip:port'
receivers='your_email_addr'  #多个邮箱间用逗号(,)分隔
skuid_dic = {'4942637':u'CPU','5113345':u'电脑','4207732':u'手机'}  #要监控的商品ID(唯一）,名称

#存放上次旧价格字典
old_price_dic = {}

#旧价格 存档文件
old_price_file = os.path.dirname(os.path.realpath(__file__)) + '/old_price.tmp'

#标志价格是否变动
is_changed = 0

#价格变动 邮件内容
mail_content = ""

# 邮件发送函数
def sendmail(title,content):
# 此处的 mail provider 用的是 open-falcon 开源组件 https://github.com/open-falcon/mail-provider.git
# 此函数根据实际情况修改
# Usage: send_mail "title" "content" "mail0,mail1,mail2"
    url = 'http://%s/sender/mail'%(mail_server)
    
    values = {'tos':receivers,
              'subject':title,
              'content':content }
    data = urllib.urlencode(values)
    curl(url,data)

    
# 网页访问函数
def curl(url,data=''):
    if data:
        req = urllib2.Request(url,data)
    else:
        req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    the_page_json = response.read()
    return the_page_json

    
#获取旧价格列表
def get_old_price():
    global old_price_dic
    if os.path.exists(old_price_file):
        file_object = codecs.open(old_price_file,'r+','UTF-8')
        try:
            old_price_list = file_object.readlines( )
            for each in old_price_list:
                if each.strip('\n'):
                    old_price_dic = dict(old_price_dic,**eval(each.strip('\n')))
        finally:
            file_object.close()

            
#写入旧价格列表
def set_old_price():
    file_object = codecs.open(old_price_file, 'w','UTF-8')
    try:
        for (k,v) in old_price_dic.items():
            file_object.write("{'%s':%s}\n"%(k,v))
    finally:
        file_object.close()


#单次获取价格
def get_price_once(id,name,old_price):
    is_changed = 0
    mail_content = ""
    old_price_dic = {}
    url = 'http://p.3.cn/prices/mgets?skuIds=%s,J_&type=1'%(id)

    try:
        data = curl(url)
        the_page_dic = json.loads(data)[0]
        price = float(the_page_dic[u'p'])
        if price < old_price :
            is_changed = 1
            logger.info('%s降价啦，降价前：%s ,降价后：%s'%(name.encode('utf-8'),old_price,price))
            mail_content = '%s降价啦，降价前：%s ,降价后：%s \n'%(name.encode('utf-8'),old_price,price)
            old_price_dic[id] = price
        elif price > old_price :
            is_changed = 1
            logger.info('%s升价啦，升价前：%s ,升价后：%s'%(name.encode('utf-8'),old_price,price))
            mail_content = '%s升价啦，升价前：%s ,升价后：%s \n'%(name.encode('utf-8'),old_price,price)
            old_price_dic[id] = price
        return is_changed,old_price_dic,mail_content
    except Exception as e:
        logger.error(e)


#各进程回调函数，收集结果
def collectMyResult(result):
    global is_changed,old_price_dic,mail_content
    if result:
        sign = result[0]
        dic = result[1]
        content = result[2]

        if sign:
            is_changed = sign
            old_price_dic.update(dic)
            mail_content += content

#包装 worker 函数，确保超时中断进程
def abortable_worker(func, *args, **kwargs):
    timeout = kwargs.get('timeout', None)
    p = ThreadPool(1) #单线程 （其实相当于一个进程，哈哈）
    res = p.apply_async(func, args=args)
    try:
        out = res.get(timeout)  # Wait timeout seconds for func to complete.
        return out
    except multiprocessing.TimeoutError:
        #print("Aborting due to timeout")
        p.terminate()  #超时终端本子线程
        raise


#woker 函数，各进程分别执行此函数,返回结果给回调函数
def worker(*cmd):
    #get_price_once(k,v,old_price)
    args = ('%s'*len(cmd)%(cmd)).split()
    if args:
        return get_price_once(args[0],args[1],float(args[2]))


# 执行命令，合并返回的结果
if __name__ == "__main__":
    get_old_price()
    pool = multiprocessing.Pool(processes = 8)
    for (k,v) in skuid_dic.items():
        old_price = 0.0
        if k in old_price_dic:
            old_price = float(old_price_dic[k])
        abortable_func = partial(abortable_worker, worker, timeout=10)  #默认超时时间为10秒
        pool.apply_async(abortable_func, args="%s %s %s"%(k,v,old_price), callback=collectMyResult)
    pool.close()
    pool.join()
    if is_changed:
        sendmail('JD商品价格变动',mail_content)
        set_old_price()

