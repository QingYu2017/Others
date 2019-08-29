```shell
Auth:Qing.Yu
Mail:1753330141@qq.com
 Ver:V1.0
Date:2019-08-29
```

### 摘要说明
基于容器的MySQL（mariadb）主从复制实验，数据通过挂载卷方式实现持久化

### 需求背景
- 通过容器满足快速部署和应用的需求；
- 通过主从复制，满足MySQL的读写分离、高可用等场景需求；

### 方案设计
1. 使用dockerfile创建MySQL镜像，实现MySQL环境的标准化配置；
1. 使用主从复制模式，实现MySQL的异步复制；

### 参考资料
- 李在弘, 武传海. Docker基础与实战[M]. 人民邮电出版社, 2016.
- 龚正. Kubernets权威指南[M]. 电子工业出版社, 2018. 
- 杨保华, 戴王剑, 曹亚仑. Docker技术入门与实战[M]. 机械工业出版社, 2015.
- Tushar S . LINUX SHELL脚本攻略(第2版)(图灵程序设计丛书)[M]. 人民邮电出版社, 2014.
- 余洪春. 构建高可用Linux服务器[M]. 机械工业出版社, 2012.

### Dokerfile
```dockerfile
#配置mariadb
# 基础镜像
FROM centos
# 作者
#MAINTAINER 1753330141@qq.com mariadb

# 配置脚本
#修改时区
RUN \cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime; \
    rpm -i http://mirrors.ustc.edu.cn/epel/7/x86_64/Packages/e/epel-release-7-11.noarch.rpm; \
    rpm -i http://mirrors.ustc.edu.cn/ius/stable/CentOS/7/x86_64/ius-release-1.0-15.ius.centos7.noarch.rpm; \
    yum -y install mariadb-server; \
    yum clean all; \
    sed -i '$a\export LANG="en_US.UTF-8"' /etc/bashrc;
# 发布端口
EXPOSE 3306
#创建容器后台运行
CMD ["/usr/sbin/init"]
```

创建测试容器并配置主从复制
```shell
#清空容器（非prod标识）
docker ps -a|grep -v "\\(prod\\)"|awk '{print $1}'|xargs -I {} docker stop {};docker ps -a|grep -v "\\(prod\\)"|awk '{print $1}'|xargs -I {} docker rm {}
#删除测试本地持久化卷
rm -rf /root/Docker_MySQL/test_och_mariadb01
#创建主服务器容器
docker run -d --name test_och_mariadb01 \
           -p 8001:3306 \
           -v /root/Docker_MySQL/test_och_mariadb01:/var/lib/mysql:rw \
           --restart=always och_mariadb 
docker exec -it test_och_mariadb01 /bin/bash -c 'chown -R mysql:mysql /var/lib/mysql && /usr/bin/mysql_install_db --user=mysql && systemctl enable mariadb && systemctl start mariadb;'
docker exec -it test_och_mariadb01 bash

#创建从服务器容器
docker run -d --name test_och_mariadb02 \
           -p 8002:3306 \
           -v /root/Docker_MySQL/test_och_mariadb02:/var/lib/mysql:rw \
           --link test_och_mariadb01 \
           --restart=always och_mariadb 
docker exec -it test_och_mariadb02 /bin/bash -c 'chown -R mysql:mysql /var/lib/mysql && /usr/bin/mysql_install_db --user=mysql && systemctl enable mariadb && systemctl start mariadb;'
docker exec -it test_och_mariadb02 bash

#主服务器变更设置
sed '1 aserver_id=8001\nalog-bin=master8001' -i /etc/my.cnf
systemctl restart mariadb
echo 'grant replication slave on *.* to repluser@"%" identified by "123456";flush privileges;'|mysql -uroot

#从服务器变更设置
sed '1 aserver_id=8002' -i /etc/my.cnf
systemctl restart mariadb
echo "change master to master_host=\"test_och_mariadb01\" ,master_port=3306 ,master_user=\"repluser\" ,master_password=\"123456\" ,master_log_file=\"master8001.000001\" ,master_log_pos=245;start slave;show slave status\\G;"|mysql -uroot
```
![示例](https://github.com/QingYu2017/pic/blob/master/201908290001.png)

### 问题总结
- MySQL容器挂载宿主机卷后，需要对MySQL初始化，要留意权限设置、服务器启停的顺序控制；
- 容器间通信如果选择宿主机端口转发，同一宿主机上多容器内部端口相同时，会存在通信异常，如宿主机10.166.10.12，01容器8001:3306，02容器8002:3306，
容器02执行mysql -h10.166.10.12 --port=8001 -urepluser -p123456，访问01容器的发布端口，无法正常通信。
可以在创建02容器时，添加--link放通02容器和01容器的通信

### 致谢
感谢Stanley的友情支持和耐心答疑
