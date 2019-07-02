## data model and promQL

prometheus metric 是由一个度量名称和一组标签组成的多维数据模型，并且由一个度量名称和一组标签唯一标识，用于描述一条监控数据。

格式如下:

```
< metric name >{ <label name>=<label value>, ...}
```

例如：

```
up{ hostname="overcloud-controller-0.localdomain",instance="172.17.1.18:9100",job="node_exporter",node_role="control"}
```

在这条metric中, 'up' 代表度量名称, `{hostname="overcloud-controller-0.localdomain"，....}` 代表标签组。标签可用于条件查询，数据聚合等操作。

Prometheus提供了PromQL用于数据查询:

```
query=up{hostname="overcloud-controller-0.localdomain"}，查询主机overcloud-controller-0 下所有job/exporter的状态，这是prometheus中的条件语句。
query=up，查询所有job/exporter的状态。
```

## how to use prometheus api

我们在Prometheus服务器上的`/api/v1`下可以访问当前稳定的HTTP API, prometheus返回的数据格式为json，下边的返回值中value=0表明该job/exporter状态是down，value=1表明该job/exporter正常工作。

调用API获取主机overcloud-controller-0 下所有job/exporter的状态：`http://192.168.2.120:9091/api/v1/query?query=up{overcloud-controller-0.localdomain}`:

```
curl http://192.168.2.120:9091/api/v1/query?query=up{overcloud-controller-0.localdomain}
{
    "status":"success",
    "data":{
        "resultType":"vector",
        "result":[
            {
                "metric":{
                    "__name__":"up",
                    "hostname":"overcloud-controller-0.localdomain",
                    "instance":"172.17.1.18:9100",
                    "job":"node_exporter",
                    "node_role":"control"
                },
                "value":[
                    1562060360.346,
                    "1"
                ]
            },
            {
                "metric":{
                    "__name__":"up",
                    "hostname":"overcloud-controller-0.localdomain",
                    "instance":"172.17.1.18:9101",
                    "job":"prometheus"
                },
                "value":[
                    1562060360.346,
                    "1"
                ]
            }
        ]
    }
}
```

Prometheus API详细用法可参考：[Prometheus API 官方指南](https://prometheus.io/docs/prometheus/latest/querying/api/#expression-queries)

## prometheus aggregation operators

prometheus 支持聚合操作。下面用两个例子说明。

**count:** 获取所有job/exporter的总数，只需调用count操作符即可：count(up)

**without or by :** 若要保留一些label我们可以配合使用 without 或者 by 操作符， 如count(up) by (hostname) 表示每一台host下的job/exporter总数。without与by相反，是剔除某些lable。

prometheus 聚合操作符请参考官方指南：[Prometheus aggregation operators](https://prometheus.io/docs/prometheus/latest/querying/operators/#aggregation-operators)

另外prometheus提供了一些函数用于数据处理。例如求网络端口发送/接收速率就用到了irate函数。

prometheus 提供的函数详细使用请参考官方指南：[prometheus functions](https://prometheus.io/docs/prometheus/latest/querying/functions/)

## how to retrieve metrics in related openstack

以下是一些metric的获取方式

#### 主机

- 主机序列号: /api/v1/query?query=node_info{hostname='overcloud-controller-0.localdomain'} # 标签serial即序列号

- 所有主机名: /api/v1/label/hostname/values

- CPU使用率:

  - 总使用率：/api/v1/query?query=sum(os_nova_hypervisor_vcpus_used) /sum(os_nova_hypervisor_vcpus_total)

  - 各host cpu 使用率：/api/v1/query?query=sum(os_nova_hypervisor_vcpus_used) by (hostname)/sum(os_nova_hypervisor_vcpus_total) by (hostname)

- 总CPU数量：/api/v1/query?query=count(node_cpu_seconds_total{mode="idle"})

- 内存使用率: /api/v1/query?query=(node_memory_MemTotal_bytes-node_memory_MemAvailable_bytes)/node_memory_MemTotal_bytes

- 总内存: /api/v1/query?query=node_memory_MemTotal_bytes

- 已用内存：/api/v1/query?query=node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes

- 网络端口发送速率：/api/v1/query?query=irate(node_network_receive_bytes_total)[10m])

- 网络端口接收速率：/api/v1/query?query=irate(node_network_transmit_bytes_total[10m])

#### 虚拟机

- CPU使用率: /api/v1/query?query=irate(os_instance_cpu_cpu_time{instance_name="test"}[5m])/1e+9

- 总CPU数量: /api/v1/query?query=os_instance_cpu_vcpus{instance_uuid=""}

- 内存使用率: /api/v1/query?query=os_instance_memory_used{instance_uuid=""}/os_instance_memory_actual{instance_uuid=""}

- 总内存：/api/v1/query?query=os_instance_memory_actual{instance_uuid=""}

- 已用内存：/api/v1/query?query=os_instance_memory_used{instance_uuid=""}

- 硬盘读出速率：/api/v1/query?query=irate(os_instance_disk_read_bytes{instance_uuid=""}[5m])

- 硬盘写入速率：/api/v1/query?query=irate(os_instance_disk_write_bytes{instance_uuid=""}[5m])

- 硬盘读出IOPS：/api/v1/query?query=irate(os_instance_disk_read_requests_issued{instance_uuid=""}[5m])

- 硬盘写入IOPS：/api/v1/query?query=irate(os_instance_disk_write_requests_issued{instance_uuid=""}[5m])

- 网络端口发送速率：/api/v1/query?query=irate(os_instance_interface_net_read_bytes{instance_uuid=""}[5m])

- 网络端口接收速率：/api/v1/query?query=irate(os_instance_interface_net_write_bytes{instance_uuid=""}[5m])
