from argparse import ArgumentParser
from enum import Enum
from ipaddress import IPv4Address, IPv6Address, ip_address
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Union

parser = ArgumentParser(
    prog='openwrt-iptables-forward-adder',
    description='Openwrt 添加 iptables IP 转发的小工具 / The tools for adding iptables IP forwarding rules on Openwrt',
    epilog='版权信息 / Copyright: Lovemilk (zhuhansan666@github), BSD 3-Clause License\n'
           'https://github.com/zhuhansan666/openwrt-iptables-forward-adder',
)


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
    id: float
    create_at: datetime = field(default_factory=lambda: datetime.now())

    def __hash__(self):
        return int(self.id)

    @classmethod
    def from_jsonable_metadata(cls, metadata: 'JsonableMetadata'):
        metadata_dict = asdict(metadata)
        return cls.from_json(metadata_dict)

    @classmethod
    def from_json(cls, metadata_dict: dict):
        metadata_dict['destination_ip'] = ip_address(metadata_dict['destination_ip'])
        metadata_dict['protocol'] = Protocols(metadata_dict['protocol'])
        metadata_dict['create_at'] = datetime.fromisoformat(metadata_dict['create_at'])

        return cls(**metadata_dict)


@dataclass
class JsonableMetadata(Metadata):
    destination_ip: Union[IPv4Address, IPv6Address, str]
    id: float = None
    create_at: Union[datetime, str] = field(default_factory=lambda: datetime.now())

    def __post_init__(self):
        self.id = self.create_at.timestamp() if self.id is None else self.id
        self.destination_ip = str(self.destination_ip)
        self.create_at = self.create_at.isoformat()
