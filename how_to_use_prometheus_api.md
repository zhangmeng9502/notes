## data model and promQL
prometheus metric 是由一个度量名称和一组标签组成，并且由一个度量名称和一组标签唯一标识的时间序列: < metric name >{ < label name >=< label value >, ...}。

例如：某个prometheus job/exporter的状态由'up'这个度量名称和{job='job1',instance='instance1'...}一组标签唯一标识。标签可以用于条件筛选以及数据聚合等操作。例如up{hostname="overcloud-controller-0.localdomain"}表示主机overcloud-controller-0下所有job/exporter状态。

Prometheus提供了PromQL用于查询数据。query=up{hostname="overcloud-controller-0.localdomain"}，prometheus返回主机overcloud-controller-0 下所有job/exporter的状态，这就是prometheus中的条件语句。若query=up，prometheus将返回所有job/exporter的状态。

## how to use prometheus api
我们在Prometheus服务器上的/api/v1下可以访问当前稳定的HTTP API, prometheus返回的数据格式为json，下边的返回值中value=0表明该job/exporter状态是down，value=1表明该job/exporter正常工作。

调用API获取主机overcloud-controller-0 下所有job/exporter的状态：http://192.168.2.120:9091/api/v1/query?query=up{overcloud-controller-0.localdomain}

返回值:

{"status":"success","data":{"resultType":"vector","result":[{"metric":{"__name__":"up","hostname":"overcloud-controller-0.localdomain","instance":"172.17.1.18:9100","job":"node_exporter","node_role":"control"},"value":[1562060360.346,"1"]},{"metric":{"__name__":"up","hostname":"overcloud-controller-0.localdomain","instance":"172.17.1.18:9101","job":"prometheus"},"value":[1562060360.346,"1"]}]}}


API 调用可参考官方指南：
https://prometheus.io/docs/prometheus/latest/querying/api/#expression-queries

## prometheus aggregation operators
prometheus 支持聚合操作。下面用两个例子说明。

count:
获取所有job/exporter的总数，只需调用count操作符即可：count(up)。

without or by :
若要保留一些label我们可以配合使用 without 或者 by 操作符， 如count(up) by (hostname) 表示每一台host下的job/exporter总数。without与by相反，是剔除某些lable。

关于聚合操作的官方指南：https://prometheus.io/docs/prometheus/latest/querying/operators/#aggregation-operators

另外prometheus提供了一些函数用于数据处理。例如求网络端口发送/接收速率就用到了irate函数。详细使用请参考官方指南：https://prometheus.io/docs/prometheus/latest/querying/functions/。

## how to retrieve metrics in related openstack
以下是一些metric的获取方式
#### 主机
主机序列号: /api/v1/label/serial/values

主机名: /api/v1/label/hostname/values

CPU使用率: /api/v1/query?query=node_load1

总CPU数量：/api/v1/query?query=count(node_cpu_seconds_total{mode="idle"})

内存使用率: /api/v1/query?query=(node_memory_MemTotal_bytes-node_memory_MemAvailable_bytes)/node_memory_MemTotal_bytes

总内存: /api/v1/query?query=node_memory_MemTotal_bytes

已用内存：/api/v1/query?query=node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes

网络端口发送速率：/api/v1/query?query=irate(node_network_receive_bytes_total)[10m])

网络端口接收速率：/api/v1/query?query=irate(node_network_transmit_bytes_total[10m])

#### 虚拟机
CPU使用率: /api/v1/query?query=irate(os_instance_cpu_cpu_time{instance_name="test"}[5m])/1e+9

总CPU数量: /api/v1/query?query= os_instance_cpu_vcpus{instance_uuid=""}

内存使用率: /api/v1/query?query=os_instance_memory_used{instance_uuid=""}/os_instance_memory_actual{instance_uuid=""}

总内存：/api/v1/query?query=os_instance_memory_actual{instance_uuid=""}

已用内存：/api/v1/query?query=os_instance_memory_used{instance_uuid=""}

硬盘读出速率：/api/v1/query?query=irate(os_instance_disk_read_bytes{instance_uuid=""}[5m])

硬盘写入速率：/api/v1/query?query=irate(os_instance_disk_write_bytes{instance_uuid=""}[5m])

硬盘读出IOPS：/api/v1/query?query=irate(os_instance_disk_read_requests_issued{instance_uuid=""}[5m])

硬盘写入IOPS：/api/v1/query?query=irate(os_instance_disk_write_requests_issued{instance_uuid=""}[5m])

网络端口发送速率：/api/v1/query?query=irate(os_instance_interface_net_read_bytes{instance_uuid=""}[5m])

网络端口接收速率：/api/v1/query?query=irate(os_instance_interface_net_write_bytes{instance_uuid=""}[5m])