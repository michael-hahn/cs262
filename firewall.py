import iptc

def drop_all_from(source, interface, protol):
	'''
	Drop all the packets from the IP address <source> coming in on the interface <interface> using the protocol <protol>.
	Arguments:
	source: a string of source IP address such as "255.255.255.0"
	interface: a string of interface such as "eth0"
	protol: a string of protocol used by the incoming package such as "tcp"
	'''
	chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), "INPUT")
	rule = iptc.Rule()
	rule.in_interface = interface	# Use "eth+" for any of the `eth` interfaces
	rule.src = source
	rule.protocol = protol
	rule.create_target("DROP")
	chain.insert_rule(rule)

