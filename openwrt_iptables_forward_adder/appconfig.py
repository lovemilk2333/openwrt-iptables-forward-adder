HEADER = '# __openwrt_iptables_forward_adder_metadata__: {json_string}\n'
END = '\n# __end_openwrt_iptables_forward_adder__'

FORWARD_TEMPLATE = '''\
iptables -t nat -A PREROUTING -p {protocol} --dport {source_port} -j DNAT \
--to-destination {destination_ip}:{destination_port}
iptables -t filter -A FORWARD -p {protocol} -d {destination_ip} --dport {destination_port} -m \
state --state NEW,ESTABLISHED,RELATED -j ACCEPT'''
