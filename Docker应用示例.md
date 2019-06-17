```shell
Auth:Qing.Yu
Mail:1753330141@qq.com
 Ver:V1.0
Date:2019-06-17
```
### 摘要说明
运用容器，轻便部署爬虫主机、云盘（Seafile）主机、堡垒机（teleport）、KMS主机，其中：
- 爬虫示例演示了只读方式挂载定时任务、任务脚本。
- Seafile示例演示了挂在宿主机目录，以及通过宿主机和容器之间文件转移。
- 跳板机演示了历史数据目录的挂载。
- redis示例最简单，仅开放服务端口映射。
- kms示例同redis，仅开放服务端口映射。

### 参考资料
- 李在弘, 武传海. Docker基础与实战[M]. 人民邮电出版社, 2016.
- 杨保华, 戴王剑, 曹亚仑. Docker技术入门与实战[M]. 机械工业出版社, 2015.
- Tushar S . LINUX SHELL脚本攻略(第2版)(图灵程序设计丛书)[M]. 人民邮电出版社, 2014.

### 功能示例
#### 创建爬虫容器，挂载定时任务列表及任务脚本
```shell
#创建tools容器，包含行情信息爬虫，OA通知提醒
#10.166.20.224，容器脚本和任务列表保存在宿主机/root/Docker_Docs/c_och_tools01/c_och_tools01目录
#crontab_root为任务列表，脚本在Script目录中，通过映射方式挂载给容器使用（只读方式）
docker run -d --name prod_och_tools01 \
           -v /root/Docker_Docs/c_och_tools01/crontab_root:/var/spool/cron/root:ro \
           -v /root/Docker_Docs/c_och_tools01/Script/:/root/Script/:ro \
           --restart=always och_tools
#登录容器
docker exec -it prod_och_tools01 bash
```

#### seafile（云盘）服务器
```shell
#创建seafile容器
#10.166.10.20，创建文件挂载路径/opt/Seafile_Data
#初始化的时候先创建容器不挂载目录，创建后将容器内的数据盘目录拷贝出
#cd /opt/Seafile/seafile-server-*
#./seahub.sh stop && ./seahub.sh start
#配置完管理员账号/密码后，再次关闭容器，准备拷贝
#docker cp test_och_seafile01:/opt/Seafile /opt/Seafile_Data/och_seafile01/
#有存量数据时可以挂载历史数据，直接启动服务
docker run -d -p 8000:8000 -p 8082:8082 -p 3306:3306 \
           -v /opt/Seafile_Data/och_seafile01/:/opt/Seafile/:rw \
           --restart=always \
           --name prod_och_seafile01 och_seafile /usr/sbin/init
```

#### 堡垒机（跳板机）
```shell
#创建跳板机容器
#10.166.10.21，该堡垒机挂载原非容器部署堡垒机历史数据，迁移或备份时处理/usr/local/teleport/data/
docker run -d -p 7190:7190 -p 52089:52089 -p 52189:52189 -p 52389:52389 \
           -v /opt/Docker_Data/Teleport_Data_21/data:/usr/local/teleport/data/:rw \
           --restart=always \
           --name prod_och_teleport01 och_teleport
#如宿主机磁盘足够，可以映射路径(宿主机添加/root/folder4replay/用于映射录像)，该脚本可用于测试或临时使用
docker run -d -p 7190:7190 -p 52089:52089 -p 52189:52189 -p 52389:52389 \
           -v /root/folder4replay:/usr/local/teleport/data/replay:rw \
           --restart=always \
           --name prod_och_teleport01 och_teleport
```

#### 创建redis服务器
```shell
#创建redis容器，提供本地端口映射的redis服务
#10.166.20.224
docker run -d -p 6379:6379 \
           --restart=always \
           --name prod_och_redis01 och_redis
```

#### kms服务器
```shell
#创建kms容器，提供本地端口映射的kms激活服务
#10.166.10.11
docker run -d -p 1688:1688 \
           --restart=always \
           --name prod_och_kms01 och_kms
```
