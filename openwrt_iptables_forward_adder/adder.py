import argparse
from sys import platform
from ipaddress import ip_address, IPv4Address, IPv6Address
from pathlib import Path
from enum import Enum
from json import dumps, loads
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Union

from .appconfig import HEADER, END, FORWARD_TEMPLATE


class Protocols(str, Enum):
    TCP = 'tcp'
    UDP = 'udp'
    ICMP = 'icmp'


@dataclass
class Metadata:
    name: str
    source_port: int
    destination_port: int
    destination_ip: Union[IPv4Address, IPv6Address]
    protocol: Protocols
    create_at: datetime = field(default_factory=lambda: datetime.now())


@dataclass
class JsonableMetadata:
    name: str
    source_port: int
    destination_port: int
    destination_ip: str
    protocol: Protocols
    create_at: str = field(default_factory=lambda: datetime.now().isoformat())


def generate_iptables_rules(_args: argparse.Namespace) -> str:
    _rules = FORWARD_TEMPLATE.format(
        protocol=_args.protocol,
        source_port=_args.source_port,
        destination_port=_args.destination_port,
        destination_ip=_args.destination_ip,
    )

    metadata = JsonableMetadata(
        name=_args.name, source_port=_args.source_port,
        destination_port=_args.destination_port, destination_ip=str(_args.destination_ip), protocol=_args.protocol
    )
    return HEADER.format(json_string=dumps(asdict(metadata))) + _rules + END


def write_iptables_rules(_rules: str, iptables_file: Path):
    try:
        with iptables_file.open('w', encoding='u8') as fp:
            fp.write('\n')
            fp.write(_rules)
            fp.write('\n')
    except PermissionError as e:
        print(f'permission denied / 写入失败: {e}')
        raise


def str2port(string: str) -> int:
    port = int(string)
    if not 0 <= port <= 65535:
        raise ValueError(f"port must be between 0 and 65535")
    return port


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser(
        prog='openwrt-iptables-forward-adder',
        description='Openwrt 添加 iptables IP 转发的小工具 / The tools for adding iptables IP forwarding rules on Openwrt',
        epilog='版权信息 / Copyright: Lovemilk (zhuhansan666@github), BSD 3-Clause License\n'
               'https://github.com/zhuhansan666/openwrt-iptables-forward-adder',
    )

    parser.add_argument(
        '-a', '--ignore-platform', dest="ignore_platform", action='store_true',
        help='在不受支持的平台仍然运行 / ignore whether the current platform is supported or not'
    )
    parser.add_argument(
        '-n', '--name', dest='name', type=str, required=True,
        help='转发名称 (仅供人类阅读) / the name of the iptables forwarding rule'
    )
    parser.add_argument(
        '-s', '--source-port', dest='source_port', type=str2port, required=True,
        help='源端口 (当前设备入站端口即外部端口) / source port'
    )
    parser.add_argument(
        '-d', '--destination-port', dest='destination_port', type=str2port, required=True,
        help='目标端口 (目标服务端口) / destination port'
    )
    parser.add_argument(
        '-i', '--destination-ip', dest='destination_ip', type=ip_address, required=True,
        help='目标IP (目标服务IP) / destination ip'
    )
    parser.add_argument(
        '-p', '--protocol', dest='protocol', type=Protocols, required=True,
        help='转发协议 / protocol'
    )
    parser.add_argument(
        '-f', '-iptables-file', dest='iptables_file', type=Path, default='/etc/firewall.user',
        help='iptables 配置文件路径 / iptables config file'
    )

    args = parser.parse_args()
    assert args.ignore_platform or (platform == 'linux' and platform == 'darwin'), '当前平台不受支持 / unsupported platform'
    assert args.iptables_file.is_file(), '无效 iptables 文件 / iptables file must be file'

    if args.source_port <= 1024:
        print(f'警告: 源端口 小于等于 1024, 可能需要root权限')
        print(f'WARNING: source port <= 1024, '
              f'may you need to run this program as root user')

    rules = generate_iptables_rules(args)
    print()
    print('规则生成成功, 请确认规则是否正确:')
    print('Please make sure generated rules is correct:')
    print()
    print(rules)
    print()

    assert input('是否写入文件? / Write rules (Y/n): ').lower() == 'y', \
        '用户结束操作 / user interrupted'

    write_iptables_rules(rules, args.iptables_file)

    print('文件写入成功~ 本程序结束后键入 `/etc/init.d/firewall restart` 并运行以应用规则')
    print('Rules wrote, please run `/etc/init.d/firewall restart` to restart firewall')
    print()
    print('感谢使用')
    print('Thanks for your running')
