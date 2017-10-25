# jd_price_mon

#### 作用：监测 JD（京东商城）商品价格

要监控的商品ID 可在商品展示页面的 URL 里获取,如下图：
![image](https://github.com/gujifly/jd_price_mon/blob/master/resources/%E5%95%86%E5%93%81ID%E8%8E%B7%E5%8F%96.png)

<br>
#### 需自定义：

23 ~ 25 ， 设置自己的mail-provider IP:端口 ， 收信邮箱地址列表，要监控价格的商品列表（字典）
![image](https://github.com/gujifly/jd_price_mon/blob/master/resources/%E5%8F%82%E6%95%B0%E4%BF%AE%E6%94%B9.png)

<br>
这里 mail provider 用的是 open-falcon 的开源组件 mail-provider , git地址： https://github.com/open-falcon/mail-provider.git

如果已有自己的 mail provider , 按照实际情况修改 40 ~ 50 行代码即可。
![image](https://github.com/gujifly/jd_price_mon/blob/master/resources/%E9%82%AE%E4%BB%B6%E5%8F%91%E9%80%81%E5%87%BD%E6%95%B0.png)

<br>

#### 定时运行
这个不用多说，crontab 写上一行计划任务即可，如：
```shell
* * * * * ( /usr/local/bin/python /root/get_price.py >/dev/null 2>&1 )  

