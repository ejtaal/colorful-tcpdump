#!/bin/bash

OUTPUT=02-tor-ctd-data.json
SOURCE=tor-relays.txt
# For dev:
URL="https://onionoo.torproject.org/details?limit=5&fields=or_addresses,city_name,dir_address,running,flags,exit_addresses"
# For realzies:
URL="https://onionoo.torproject.org/details?fields=or_addresses,city_name,dir_address,running,flags,exit_addresses"
URL="https://onionoo.torproject.org/details?fields=or_addresses,dir_address,running,flags,exit_addresses"

#wget -O "$SOURCE" "$URL"

jq '.relays | map(select(.flags[] | contains ("Guard"))) | .[] | .or_addresses[], .dir_address, .exit_address' | \
	perl -p -e 's/]:\d+"],//' | \
	perl -p -e 's/(\.\d+):\d+"/$1/' | \
	less
	#tr -d '"[]{' | cut -f 2 -d: | \
	#sed -e 's/^/"/' -e 's/$/\/32", "GUARD"
exit 88

echo -e '\t"TOREXIT": [' | tee "$OUTPUT"
awk "BEGIN{
	while( (getline t < ARGV[1]) > 0)last++;close(ARGV[1])}
		{print \"\t[\\\"\" \$0 \"/32\\\", \\\"\\\"]\", ((last==FNR)?\"\n\t]\n\":\",\")}" $SOURCE | \
			tee -a "$OUTPUT"

#sed -e "s/^/\t'/" -e "s/$/': '',"

https://onionoo.torproject.org/details?search=running:true
https://metrics.torproject.org/rs.html#search/running:true%20flag:guard
https://onionoo.torproject.org/details?search=running:true%20flag:guard
https://metrics.torproject.org/rs.html#search/running:true%20flag:exit
