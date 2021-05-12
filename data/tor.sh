#!/bin/bash

OUTPUT=02-tor-ctd-data.json
SOURCE=tor-relays.txt
# For dev:
URL="https://onionoo.torproject.org/details?limit=5&fields=or_addresses,city_name,dir_address,running,flags,exit_addresses"
# For realzies:
URL="https://onionoo.torproject.org/details?fields=or_addresses,city_name,dir_address,running,flags,exit_addresses"
URL="https://onionoo.torproject.org/details?fields=or_addresses,dir_address,running,flags,exit_addresses"

#wget -O "$SOURCE" "$URL"

> /tmp/p

# https://tor.stackexchange.com/questions/423/what-are-good-explanations-for-relay-flags
for flag in Guard Exit BadExit Valid Authority; do
	cat "$SOURCE" | \
		jq ".relays | map(select(.flags[] | contains (\"$flag\"))) | .[] | .or_addresses[], .dir_address, .exit_address" | \
		grep -v null | \
		sort -V | \
		perl -p -e 's#"([\.\d]+):\d+"#$1/32#' | \
		perl -p -e 's#"\[([:\.a-f\d]+)\]:\d+"#$1/128#' | \
		sed "s/\$/ $flag/" | \
		cat >> /tmp/p
done

echo -e '\t"TOR": [' | tee "$OUTPUT"
awk "BEGIN{
	while( (getline t < ARGV[1]) > 0)last++;close(ARGV[1])}
		{print \"\t[\\\"\" \$1 \"\\\", \\\"\" \$2 \"\\\"]\", ((last==FNR)?\"\n\t]\n\":\",\")}" /tmp/p | \
			tee -a "$OUTPUT"
