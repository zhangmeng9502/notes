### kolla-ansible 部署openstack

#### 主机需求：
- 物理机/虚拟机
- network interface：*2
- memory 8G 
- disk space: 40G

基础环境准备：

1. 下载eple源
```
yum install epel-release -y
```
2.安装python依赖包
```
yum install python-devel libffi-devel gcc openssl-devel libselinux-python
```
3. update pip
```
pip install -U pip
```
注：这里如果下载慢可以google下如何更换pip源，可以参考：
https://blog.csdn.net/lambert310/article/details/52412059
这一步需要你去学习pip源是什么东西？简单的说就是一个软件包仓库，与yum源相似，pip源里都是PyPI上托管的软件包，我们可以使用pip命令行install/uninstall/update

4. 安装ansible
```
    pip install ansible
```
安装 openstack(开发模式)

1.创建存放kolla配置文件的目录
```
    mkdir -p /etc/kolla
```
2.拷贝password，global文件
```  
    cp -r /usr/share/kolla-ansible/etc_examples/kolla/* /etc/kolla
    cp /usr/share/kolla-ansible/ansible/inventory/* .
```
3. 拷贝host文件
```
    cp /usr/local/share/kolla-ansible/ansible/inventory/* /root/
```
4. 克隆kolla，kolla-ansible
```
    git clone https://github.com/openstack/kolla -b stable/rocky
    git clone https://github.com/openstack/kolla-ansible -b stable/rocky
```
5. 下载依赖包
```
    pip install -r kolla/requirements.txt
    pip install -r kolla-ansible/requirements.txt
```
6. 编辑global.yml,配置相关变量
```
    vim /etc/kolla/globals.yml
```
以下三条copy到你的global.yml
```
    kolla_base_distro: "centos"
    kolla_install_type: "source"
    openstack_release: "rocky"
```
以下两条根据你的网卡名字填写
```
    network_interface: "eth0"
    neutron_external_interface: "eth1"
```
以下是你要装哪些服务，yes是安装，no是不安装；第一次装可以把下边写的这几个关掉，循序渐进。
```
    enable_ceph: "no"
    enable_cinder: "no"
    enable_haproxy: "no"
    enable_heat: "no"
    enable_neutron_agent_ha: "no"
```
7. 编辑ansible.cfg
```
    vim /etc/ansible/ansible.cfg
```
把下边的内容贴进去
```
    [defaults]
    host_key_checking=False
    pipelining=True
    forks=100
```
8. 生成password
```
    cd kolla-ansible/tools
    ./generate_passwords.py
```
9. 架构

all in one：在步骤10直接指定all-in-one文件即可

multinode：
假设你想部署的是3控制+3计算，hostname如下:
- control-node : ctl0, ctl1, ctl2
- compute-node : comp0, comp1, comp2

9.1 确认部署节点能够免密钥登录其他节点
参考：https://www.jianshu.com/p/e9db116fef8c
9.2 将hostname与ip的对应关系写入hosts文件,根据实际环境写，for example：

vim /etc/hosts
```
    127.0.0.1 localhost
    ::1     localhost localhost.localdomain localhost6 localhost6.localdomain6
    10.0.0.10 ctl0
    10.0.0.11 ctl1
    10.0.0.12 ctl2
    10.0.0.20 comp0
    10.0.0.21 comp1
    10.0.0.22 comp2
```
9.3 根据实际环境填写角色
vim /root/multinode
```
[control]
ctl0
ctl1
ctl2
# Ansible supports syntax like [10:12] - that means 10, 11 and 12.
# Become clause means "use sudo".

[network:children]
control
# when you specify group_name:children, it will use contents of group specified.

[compute]
comp0
comp1
comp2

[monitoring]
# 10.0.0.10
# This group is for monitoring node.
# Fill it with one of the controllers' IP address or some others.

[storage:children]
compute

[deployment]
localhost       ansible_connection=local become=true
# use localhost and sudo

```


10.最重要的一步到了，开发环境一定要进入到kolla-ansible的tools目录下执行

all-in-one环境：

bootstrap会安装一些基础包

    ./kolla-ansible -i /root/all-in-one bootstrap-servers

prechecks 会做一些你配置上的检查

    ./kolla-ansible -i /root/all-in-one prechecks

deploy就开始安装openstack了，等待吧

    ./kolla-ansible -i /root/all-in-one deploy
    
multinode环境：

bootstrap会安装一些基础包

    ./kolla-ansible -i /root/multinode bootstrap-servers

prechecks 会做一些你配置上的检查

    ./kolla-ansible -i /root/multinode prechecks

deploy就开始安装openstack了，等待吧

    ./kolla-ansible -i /root/multinode deploy
