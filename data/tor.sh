#!/bin/bash

. ~/scripts/generic-linux-funcs.sh

MAX_CACHE_AGE=$((7*24*60))

DETAILS_OUTPUT="tor-relay-details.txt"
#DETAILS_URL="https://onionoo.torproject.org/details?running=true&type=relay&fields=country,guard_probability,middle_probability,exit_probability,consensus_weight,consensus_weight_fraction,advertised_bandwidth,flags,as,as_name,measured,version&search=version:0.4.7."
DETAILS_URL="https://onionoo.torproject.org/details?search=running:true"

download_if_not_older "$DETAILS_OUTPUT" "$MAX_CACHE_AGE" "$DETAILS_URL"

# And now actual CTD data

OUTPUT=02-tor-ctd-data.json
SOURCE=tor-relays.txt
# For dev:
URL="https://onionoo.torproject.org/details?limit=5&fields=or_addresses,city_name,dir_address,running,flags,exit_addresses"
# For realzies:
URL="https://onionoo.torproject.org/details?fields=or_addresses,city_name,dir_address,running,flags,exit_addresses"
URL="https://onionoo.torproject.org/details?fields=or_addresses,dir_address,running,flags,exit_addresses"

download_if_not_older "$SOURCE" "$MAX_CACHE_AGE" "$URL"

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
