# openwrt-iptables-forward-adder
> Openwrt 添加 iptables IP 转发的小工具

## 使用方法
###  添加转发规则
```shell
python -m openwrt_iptables_forward_adder.adder -s <外部端口> -d <内部端口> -i <内部IP> -p <转发协议> -n <转发名称 (仅供阅读)>
```
例: 添加一个 `8000` 端口并使用 `tcp` 转发到 `192.168.1.100:9000` (转发名称可随意填写, 但为确保可读性, 应当保留适当信息)
```shell
python -m openwrt_iptables_forward_adder.adder -s 8000 -d 9000 -i 192.168.1.100 -p tcp -n test
```
