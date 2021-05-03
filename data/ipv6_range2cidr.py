#!/usr/bin/env python3

# To test:
# $0 '2001:418:1401:e::' '2001:418:1401:f:ffff:ffff:ffff:ffff'

import sys
import ipaddress

for obj in [ipaddr for ipaddr in ipaddress.summarize_address_range(ipaddress.IPv6Address( sys.argv[1]),ipaddress.IPv6Address(sys.argv[2]))]:
	print( obj)

exit(0)
