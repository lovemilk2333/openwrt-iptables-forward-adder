# openwrt-iptables-forward-adder
> Openwrt 添加 iptables IP 转发的小工具

## 使用方法
### 拉取项目
使用 `git clone` 将本项目拉取到本地
```shell
git clone https://github.com/zhuhansan666/openwrt-iptables-forward-adder.git 
```

### 更换工作目录
```shell
cd ./openwrt-iptables-forward-adder
```

### 安装依赖包
```shell
python -m pip install -r ./requirements.txt
```

###  添加转发规则
```shell
python -m openwrt_iptables_forward_adder.adder -s <外部端口> -d <内部端口> -i <内部IP> -p <转发协议> -n <转发名称 (仅供阅读)>
```
例: 添加一个 `8000` 端口并使用 `tcp` 转发到 `192.168.1.100:9000` (转发名称可随意填写, 但为确保可读性, 应当保留适当信息)
```shell
python -m openwrt_iptables_forward_adder.adder -s 8000 -d 9000 -i 192.168.1.100 -p tcp -n test
```

### 列出所有转发规则
```shell
python -m openwrt_iptables_forward_adder.editor -b list
```
示例返回:
```text
                                                                                                                                                                     
  名称 / Name    唯一标识符 / ID    源端口 / Source port   目标地址:端口 / Destination ip:port   协议 / Protocol   创建时间 (本地时间) / Create at (use local time) 
 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
     test1      1719721678.415108           8000                   192.168.1.100:9000                  tcp                       2024-06-30 12:27:58
     test2      1719813441.652832           8000                   192.168.1.100:9000                  tcp                       2024-07-01 13:57:21

```

### 删除指定转发规则
```shell
python -m openwrt_iptables_forward_adder.editor -b delete -i <规则 ID>
```
> `规则 ID` 可通过 [列出所有转发规则](#列出所有转发规则) 返回的列表获取, 位于 `唯一标识符 / ID` 项

例: 删除 ID 为 `1719721678.415108` 的转发规则
```shell
python -m openwrt_iptables_forward_adder.editor -b delete -i 1719721678.415108
```
