```shell
Auth:Qing.Yu
Mail:1753330141@qq.com
 Ver:V1.0
Date:2019-04-15
```

### 摘要说明
容器值得深入研究，尽管目前容器还不能替代对于性能、内存和网络敏感的复杂应用。但对于业务测试，以及轻量级的应用如基于内存的服务（redis和KMS），
容器具有得天独厚的优势。对于运维工作来说，也可以成倍提升系统的可靠性、灵活性，大幅降低管理成本。

### 需求背景
- 使用爬虫从互联网获取信息时，部分网站可能会使用简单的网络管理手段，对频繁发起网络请求的地址进行拦截，如果使用zbx从同一页面直接抓取数据，当目标
数据键值比较多的时候，需要多次发起访问请求，触发拦截机制。与此相似的是oracle的监控管理，如zbx直接访问oracle采集监控数据，大量性能查询会影响
oracle本身性能，干扰正常业务。
- 在使用微信企业号时，token的有效时间为3600s，如果将应用委托给外包公司管理时，将token以订阅方式提供给对方，比直接提供secretKey更为安全。
- 在桌面管理中，部分企业即便购买了正版的lic，仍然会遇到繁琐的Windows和Office激活问题，而部署kms服务器，本身也将占用windows的lic并需要进行日常管理。

### 方案设计
1. 搭建redis服务器，一次访问后将页面缓存至redis服务器，再从zbx服务器向redis请求数据，
即可轻松规避这一问题。Oracle也于此类似。
1. 在本地创建获取token的应用，并将token寄存至redis，供应用调取。
1. 配置kms镜像，支持任意平台，资源占用小，且无需二次配置。

### 参考资料
- 杨保华, 戴王剑, 曹亚仑. Docker技术入门与实战[M]. 机械工业出版社, 2015.
- Tushar S . LINUX SHELL脚本攻略(第2版)(图灵程序设计丛书)[M]. 人民邮电出版社, 2014.

### 功能示例
Widows中导入KMS镜像并映射端口，供本机激活
![示例](https://github.com/QingYu2017/pic/blob/master/2019041501.png)

### 代码参考
```python
# 基础镜像
FROM centos
# 作者
MAINTAINER Qing.Yu 1753330141@qq.com

# 配置脚本

#创建服务目录
RUN mkdir /root/kms_app
#拷贝文件
ADD kms_app /root/vlmkms_appcsdmulti/
#修改文件属性
RUN chmod a+x /root/kms_app/kms_app
#添加自动运行
RUN sed -i '$a\/root/kms_app/kms_app win' /etc/rc.d/rc.local
#修改文件属性
RUN chmod +x /etc/rc.d/rc.local
# 发布端口
EXPOSE 1688
```
