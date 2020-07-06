```shell
Auth:Qing.Yu
Mail:1753330141@qq.com
 Ver:V1.0
Date:2020-07-05
```
### 摘要说明
Zabbix可以广泛用于基础架构层面和业务系统层面的运维管理，整合Ansible、Redis、Python3等工具可以发挥更大的作用。  
Zabbix提供了多种安装方式，通过Git、yum、rpm和手动编译方式，都可以轻松的部署，同时官方也提供了容器的部署方案。  
由于容器自身存在的一些限制，比如字符集、定时任务等服务和组件的精简，还是建议在官方CentOS7镜像的基础上，自行构建开箱即用的Zabbix。  
在使用dockerfile构建过程，仍然存在一些问题，所以建议在官方镜像基础上创建容器后，执行安装脚本完成Zabbix的配置，完成后通过Docker commit创建新的镜像。  
主要问题如下：
- 构建过程中由于安全限制，无法使用systemctl start mariadb的方式启动MySQL完成后续的数据库初始化，如果使用mysqld_safe命令方式启动，执行启动命令后虽然MySQL启动成功，但是会话进程锁死，后续的镜像构建步骤停止
```shell
/usr/bin/mysqld_safe --datadir='/var/lib/mysql'
```
- 多个服务需要通过手动修改启动文件的方式设置启动，如Redis等，而运行的容器中只需要使用systemctl enalbe即可变更
- 修改时区配置需要从宿主机拷贝文件时间，而运行的容器中只需要使用timedatectl set-timezone 'Asia/Shanghai'即可变更
- 通过yum安装zabbix-server-mysql，本地在/usr/share/doc/创建目录并写入初始化脚本失败，需要rpm卸载该包后重新rpm下载安装（yum安装解决其他包的依赖关系）  

总体而言，很多问题是都是由于容器在build过程中权限和服务的差异导致，选择使用活动容器执行脚本方式完成镜像的构建

### 参考资料
- 李在弘, 武传海. Docker基础与实战[M]. 人民邮电出版社, 2016.
- 杨保华, 戴王剑, 曹亚仑. Docker技术入门与实战[M]. 机械工业出版社, 2015.
- Tushar S . LINUX SHELL脚本攻略(第2版)(图灵程序设计丛书)[M]. 人民邮电出版社, 2014.

### 初始化容器并登录
```shell
container_name=zabbix_con
docker run -d -p 20080:80 \
              -p 20051:10051 \
              --name $container_name \
              --restart=always centos:7 /usr/sbin/init 	
docker exec -it $container_name bash
```
### 容器内安装Zabbix
```shell
#install.sh
#添加wget和which组件
yum -y install wget which; \
#更改时区
timedatectl set-timezone "Asia/Shanghai"; \
#更新阿里源
wget -O /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-7.repo; \
wget -O /etc/yum.repos.d/epel.repo http://mirrors.aliyun.com/repo/epel-7.repo; \
#安装zabbix4.4源
rpm -Uvh https://mirrors.aliyun.com/zabbix/zabbix/4.4/rhel/7/x86_64/zabbix-release-4.4-1.el7.noarch.rpm; \
#更新zabbix源指向阿里源
sed -i "s/https:\/\/repo.zabbix.com\//https:\/\/mirrors.aliyun.com\/zabbix\//g" /etc/yum.repos.d/zabbix.repo
#安装中文字符集
yum -y install epel-release kde-l10n-Chinese crontabs; \
localedef -c -f UTF-8 -i zh_CN zh_CN.utf8; \
sed -i '$a\export LANG="en_US.UTF-8"' /etc/bashrc; \
sed -i -e '/MAILTO=root/a\LANG="en_US.UTF-8"' /etc/crontab; \
#安装zabbix和python3组件
yum -y install zabbix-server-mysql zabbix-web-mysql zabbix-agent redis mariadb-server python36; \
#卸载zabbix-server-mysql后单独安装，yum存在/usr/share/doc生成初始化数据库脚本写入失败的问题
rpm -qa|grep zabbix-server-mysql|xargs rpm -e; \
rpm -ivh https://mirrors.aliyun.com/zabbix/zabbix/4.4/rhel/7/x86_64/zabbix-server-mysql-4.4.10-1.el7.x86_64.rpm; \
#启动MySQL后创建zabbix账号（密码zabbix），更新授权并初始化数据库
systemctl start mariadb; \
echo "create database zabbix character set utf8 collate utf8_bin;" | mysql; \
echo "create user zabbix@localhost identified by 'zabbix';" | mysql; \
echo "grant all privileges on zabbix.* to zabbix@localhost;" | mysql; \
zcat /usr/share/doc/zabbix-server-mysql*/create.sql.gz | mysql -uzabbix -pzabbix zabbix; \
#修改server配置中的数据库密码和时区设置
sed -i '/# DBPassword=/a DBPassword=zabbix' /etc/zabbix/zabbix_server.conf; \
sed -i '/        # php_value date.timezone Europe\/Riga/a\        php_value date.timezone Asia\/Shanghai' /etc/httpd/conf.d/zabbix.conf; \
#修改redis地址绑定
sed -i 's/^bind 127.0.0.1/bind 0.0.0.0/g' /etc/redis.conf; \
#redis启动设置，通过dockerfile初始化时使用
#sed -i '$a\/usr/bin/redis-server /etc/redis.conf' /etc/rc.d/rc.local; \
#chmod +x /etc/rc.d/rc.local; \
#安装Pyhton虚拟环境并切换到v36环境（缺省2.75）
curl https://bootstrap.pypa.io/get-pip.py|python; \
pip install virtualenv virtualenvwrapper fabric --no-cache-dir -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com; \
sed -i '$a\source /usr/bin/virtualenvwrapper.sh' /etc/bashrc; \
source /usr/bin/virtualenvwrapper.sh; \
mkvirtualenv -p `which python3.6` v36; \
#安装python组件
pip install requests bs4 flask flask-bootstrap flask_restful flask-admin paramiko pymssql pymysql redis scrapy pillow numpy pandas --no-cache-dir -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com; \
#清理yum缓存
yum clean all; \
#启动服务并设置开机启动
systemctl restart zabbix-server zabbix-agent httpd redis; \
systemctl enable zabbix-server zabbix-agent httpd mariadb redis;
```
### 退出容器并提交保存为镜像
```shell
docker commit zabbix_con zabbix_img
```

### 通过镜像初始化zabbix容器，并将web端口发布为20080，zabbix通信端口
```shell
container_name=zabbix_con_new
docker run -d -p 20080:80 \
              -p 20051:10051 \
              --name $container_name \
              --restart=always zabbix_img /usr/sbin/init 	
```

通过20080端口访问Zabbix初始化之后，即可通过缺省账号/密码登录：Admin/zabbix，数据库密码zabbix
![Image text](https://github.com/QingYu2017/pic/blob/master/202007060001.png)
