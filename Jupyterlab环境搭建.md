```shell
Auth:Qing.Yu
Mail:1753330141@qq.com
 Ver:V1.0
Date:2019-09-27
```

### 摘要说明
通过Jupyterlab配置Python数据分析的环境，大致过程包括安装vscode（Windows）、python、virtualenv、numpy、pandas、scipy、matploplib等组件，熟悉的话，大约十多分钟即可完成。  
由于Python社区非常活跃，版本更新频繁，为了保证开发环境的一致性，同时方便Windows、MacOS、Linux甚至是移动端用户，通过浏览器访问获得一致的使用体验，使用容器方式部署是一种更简单便捷的可选方案。
![示例](https://github.com/QingYu2017/pic/blob/master/20190927154842.png)

### 方案设计
1. 使用dockerfile创建Jupyterlab镜像，实现标准化配置。简单说，包含下载centos官方镜像、安装Python3、安装虚拟环境、安装爬虫、web开发、Jupyterlab和数据分析相关的库。
1. 宿主机（Linux、MacOS或Windows）上根据用户分配容器，并配置独立的用户数据空间、访问密码、访问地址（端口），用户相互独立；
![示例](https://github.com/QingYu2017/pic/blob/master/20190927144045.png)

### 参考资料
- 龚正. Kubernets权威指南[M]. 电子工业出版社, 2018. 
- 杨保华, 戴王剑, 曹亚仑. Docker技术入门与实战[M]. 机械工业出版社, 2015.
- Tushar S . LINUX SHELL脚本攻略(第2版)(图灵程序设计丛书)[M]. 人民邮电出版社, 2014.
- 余洪春. 构建高可用Linux服务器[M]. 机械工业出版社, 2012.
- Lindblad T , Kinser J M . NumPy, SciPy and Python Image Library[M]// Image Processing using Pulse-Coupled Neural Networks. Springer Berlin Heidelberg, 2013.
- Pajankar A . Matplotlib[M]// Raspberry Pi Supercomputing and Scientific Programming. Apress, 2017.

### 编写Dokerfile
文件名och_jupyter.dockerfile
```dockerfile
# -*- coding: utf-8 -*- 
#Auth:Qing.Yu
#Mail:1753330141@qq.com
# Ver:V1.0
#Date:2019-09-27

# 基础镜像
FROM centos
# 作者
MAINTAINER 1753330141@qq.com 支持定时任务，包含python虚拟化境并缺省创建v36版本环境，集成常规使用的爬虫、网络管理、flask、Scrapy等常用功能，jupyterlab环境

# 配置脚本
#修改时区
RUN \cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime; \
    yum -y install crontabs; \
    rpm -i http://mirrors.aliyun.com/epel/7/x86_64/Packages/e/epel-release-7-11.noarch.rpm; \
    rpm -i http://mirrors.aliyun.com/ius/stable/CentOS/7/x86_64/ius-release-1.0-15.ius.centos7.noarch.rpm; \
    yum -y install python36 which; \
    yum clean all; \
    curl https://bootstrap.pypa.io/get-pip.py|python; \
    pip install virtualenv virtualenvwrapper fabric --no-cache-dir -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com; \
    sed -i '$a\source /usr/bin/virtualenvwrapper.sh' /etc/bashrc; \
    source /usr/bin/virtualenvwrapper.sh; \
    mkvirtualenv -p `which python3.6` v36; \
    pip install requests bs4 flask flask-bootstrap flask_restful flask-admin paramiko pymssql pymysql redis --no-cache-dir -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com; \
    pip install scrapy pillow numpy pandas matplotlib scipy Jupyterlab jupyter_contrib_nbextensions cufflinks --no-cache-dir -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com; \
    sed -i '$a\export LANG="en_US.UTF-8"' /etc/bashrc; \
    sed -i -e '/MAILTO=root/a\LANG="en_US.UTF-8"' /etc/crontab; \
    jupyter notebook --generate-config; \
    jupyter contrib nbextension install --user --skip-running-check; \    
    mkdir /root/Develop; \    
    pwd=`/root/.virtualenvs/v36/bin/python -c "import IPython;print(IPython.lib.passwd('1&34Abcd'))"`; \
    sed -i "s/\(#c.NotebookApp.password = \).*/\1u'$pwd'/" /root/.jupyter/jupyter_notebook_config.py; \
    sed -i "s/\(#c.NotebookApp.ip = \).*/\1'\*'/" /root/.jupyter/jupyter_notebook_config.py; \
    sed -i "s/\(#c.NotebookApp.open_browser = \).*/\1False/" /root/.jupyter/jupyter_notebook_config.py; \
    sed -i "s/\(#c.NotebookApp.allow_remote_access = \).*/\1True/" /root/.jupyter/jupyter_notebook_config.py; \
    sed -i "s/\(#c.NotebookApp.notebook_dir = \).*/\1'\/root\/Develop\/'/" /root/.jupyter/jupyter_notebook_config.py; \
    #开启设置
    sed -i "s/^\#c.NotebookApp.password\ /c.NotebookApp.password\ /g" /root/.jupyter/jupyter_notebook_config.py; \
    sed -i "s/^\#c.NotebookApp.ip/c.NotebookApp.ip/g" /root/.jupyter/jupyter_notebook_config.py; \
    sed -i "s/^\#c.NotebookApp.open_browser/c.NotebookApp.open_browser/g" /root/.jupyter/jupyter_notebook_config.py; \
    sed -i "s/^\#c.NotebookApp.allow_remote_access/c.NotebookApp.allow_remote_access/g" /root/.jupyter/jupyter_notebook_config.py; \
    sed -i "s/^\#c.NotebookApp.notebook_dir/c.NotebookApp.notebook_dir/g" /root/.jupyter/jupyter_notebook_config.py; \
    #随容器启动
    echo -e '[Unit]\nDescription=Jupyterlab Server\nAfter=syslog.target network.target\n\n[Service]\nUser=root\nExecStart=/root/.virtualenvs/v36/bin/jupyter lab --allow-root\nRestart=always\n\n[Install]\nWantedBy=multi-user.target' >/etc/systemd/system/jupyterlab.service; \
    systemctl enable jupyterlab.service;    
#创建容器后台运行
CMD ["/usr/sbin/init"]
```
### 启动容器
容器的开发文件目录为/root/Develop/，将宿主机的/root/Downloads/Docker_Jupyter目录挂载至此目录，如目录不存在，启动容器时会自动创建。  
并将Jupyterlab的8888访问端口，通过宿主机的8001端口发布。
```shell
docker run -d -p 8001:8888 \
    -v /root/Downloads/Docker_Jupyter/:/root/Develop/:rw \
    --restart=always \
    --name prod_och_jupyter01 och_jupyter
```

### 组件的添加和更新
如果需要在容器中添加新的组件库，可以在Jupyterlab中打开终端，激活用户配置并切换至Jupyter所在的虚拟环境后，通过pip或yum添加。
```shell
sh-4.2# source ~/.bash_profile 
[root@32d26fcac72b /]# workon v36
(v36) [root@32d26fcac72b /]# pip install matplotlib
```
![示例](https://github.com/QingYu2017/pic/blob/master/20190927144249.png)

### 问题总结
- 推荐使用的环境是Linux和MacOS，Windows平台的Docke Desktop尚不完善。在Windows中启动容器后，由于没有加载systemd启动Jupyterlab服务，需要手工启动Jupyterlab，同时Windows的Docker需要4G以上的内存。
- JupyterNotebook( http://localhost:8888/tree )可以使用cufflinks库直接生成可视化图表，Jupyterlab（ http://localhost:8888/lab ）扩展编译异常，可视化渲染暂时使用matplotlib库。
