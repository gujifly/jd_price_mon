# jd_price_mon

#### 作用：监测 JD（京东商城）商品价格

要监控的商品ID 可在商品展示页面的 URL 里获取,如下图：
![image]()

#### 需自定义：
23 ~ 25 ， 设置自己的mail-provider IP:端口 ， 收信邮箱地址列表，要监控价格的商品列表（字典）

这里 mail provider 用的是 open-falcon 的开源组件 mail-provider , git地址： https://github.com/open-falcon/mail-provider.git

如果已有自己的 mail provider , 按照实际情况修改 40 ~ 50 行代码即可。


