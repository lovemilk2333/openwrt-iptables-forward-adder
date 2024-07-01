from sys import platform
from pathlib import Path
from enum import Enum
from json import loads
from typing import Dict, List
import rich.box
from rich.console import Console
from rich.table import Table

from .appconfig import HEADER, END
from . import Metadata


class Behavior(str, Enum):
    LIST = 'list'
    DELETE = 'delete'


LineIndex = int  # 行索引, 从 0 开始
RulesDict = Dict[Metadata, List[LineIndex]]


def list_rules(iptables_file: Path) -> RulesDict:
    _header_without_metadata = HEADER.strip().split(':', 1)[0]
    keys = []
    values = []

    line_index = 0
    with iptables_file.open('r', encoding='u8') as fp:
        line = fp.readline()
        while line:
            lower_line = line.lower().strip()

            try:
                if lower_line.startswith(_header_without_metadata):
                    try:
                        json_metadata = loads(line.strip().split(':', 1)[-1])
                        metadata = Metadata.from_json(json_metadata)
                    except Exception as e:
                        print(f'加载 {line!r} 的元数据失败 / Failed to load the metadata of {line!r}: {e}')
                        continue

                    keys.append(metadata)
                    values.append([line_index, ])

                elif lower_line.startswith(END.strip()):
                    if not values or not isinstance(values[-1], list):
                        print(f'警告: 未闭合的终止标识 (位于第 {line_index + 1} 行): {line!r}')
                        print(f'WARNING: Termination identifier for unclosing (at Line {line_index + 1}): {line!r}')
                        continue

                    values[-1].append(line_index)
            finally:
                line = fp.readline()
                line_index += 1

    return dict(zip(keys, values))


def show_rules(rules: RulesDict):
    console = Console()
    table = Table(box=rich.box.SIMPLE_HEAD)

    headers = {
        '名称 / Name': '{_.name}',
        '唯一标识符 / ID': '{_.id}',
        '源端口 / Source port': '{_.source_port}',
        '目标地址:端口 / Destination ip:port': '{_.destination_ip}:{_.destination_port}',
        '协议 / Protocol': '{_.protocol}',
        '创建时间 (本地时间) / Create at (use local time)': '{formated_create_at}',
    }
    for header in headers:
        table.add_column(header, justify='center')

    for rule in rules:
        table.add_row(
            *(
                header_value.format(_=rule, formated_create_at=rule.create_at.strftime('%Y-%m-%d %H:%M:%S'))
                for header_value in headers.values()
            )
        )

    console.print(table)


def delete_from_file(iptables_file: Path, rule_lines: List[LineIndex]):
    result_lines = []

    line_index = 0
    with iptables_file.open('r', encoding='u8') as fp:
        line = fp.readline()
        while line:
            try:
                if rule_lines[0] <= line_index <= rule_lines[1]:
                    continue

                result_lines.append(line)
            finally:
                line = fp.readline()
                line_index += 1

    with iptables_file.open('w', encoding='u8') as fp:
        fp.writelines(result_lines)

def delete_rule(rule_id: float, iptables_file: Path, rules: RulesDict):
    try:
        rule_metadata, rule_lines = next(filter(lambda item: item[0].id == rule_id, rules.items()))
    except StopIteration:
        print(f'错误: 未找到 id 为 `{rule_id}` 的规则项')
        print(f'ERROR: The rule which id is `{rule_id}` not found')

        e = KeyError(str(rule_id))
        raise e.with_traceback(None)

    print('即将删除如下规则, 请确认')
    print('Will delete the following rules:')
    show_rules({rule_metadata: rule_lines})

    assert input('确认删除? / Continue? (Y/n): ').lower() == 'y', \
        '用户结束操作 / user interrupted'

    delete_from_file(iptables_file, rule_lines)

    print()
    print('删除成功~')
    print('Deleted!')


if __name__ == '__main__':
    from . import parser

    parser.add_argument(
        '-a', '--ignore-platform', dest='ignore_platform', action='store_true',
        help='在不受支持的平台仍然运行 / ignore whether the current platform is supported or not'
    )
    parser.add_argument(
        '-f', '--iptables-file', dest='iptables_file', type=Path, default='/etc/firewall.user',
        help='iptables 配置文件路径 / iptables config file'
    )
    parser.add_argument(
        '-b', '--behavior', dest='behavior', type=Behavior, required=True,
        help='脚本行为 ("list", "delete") / behavior (choices: "list", "delete")'
    )
    parser.add_argument(
        '-i', '--id', dest='delete_id', type=float, default=None,
        help='要删除的条目 ID (仅 behavior 为 `delete` 时有效) / '
             'The id you want to delete (You can only use this argument when behavior is "delete")'
    )

    args = parser.parse_args()
    assert args.ignore_platform or platform == 'linux' or platform == 'darwin', '当前平台不受支持 / unsupported platform'
    assert args.iptables_file.is_file(), '无效 iptables 文件 / iptables file must be file'

    if args.behavior == Behavior.LIST:
        show_rules(list_rules(args.iptables_file))
    elif args.behavior == Behavior.DELETE:
        assert args.delete_id is not None, ('behavior 为 `delete` 时 id 不能为空 / '
                                            'id must be provided when behavior is `delete`')
        delete_rule(args.delete_id, args.iptables_file, list_rules(args.iptables_file))

    print()
    print('感谢使用')
    print('Thanks for your running')
