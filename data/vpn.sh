#!/bin/bash

# Should end with -ctd-data.json
OUTPUT=10-vpn-ctd-data.json
SOURCE=vpn-ipranges.txt
URL="https://api.mullvad.net/www/relays/all/"

#wget -O "$SOURCE" "$URL"

> /tmp/p

jq '.[] | [.ipv4_addr_in,.city_code] | @tsv' < "$SOURCE" | \
	sed -e 's/\\t/", "/' | \
	tee -a /tmp/p

jq '.[] | [.ipv6_addr_in,.city_code] | @tsv' < "$SOURCE" | \
	sed -e 's/\\t/", "/' | \
	fgrep -v '"",' | \
	tee -a /tmp/p

echo -e '\t"MULLVAD": [' | tee "$OUTPUT"
awk 'BEGIN{
	while( (getline t < ARGV[1]) > 0)last++;close(ARGV[1])}
	{print "\t[" $0 "]", ((last==FNR) ? "\n\t]\n" :",")}' /tmp/p | \
		tee -a "$OUTPUT"

#awk "BEGIN{
#	while( (getline t < ARGV[1]) > 0)last++;close(ARGV[1])}
#		{print \"\t\\\"\" \$0 \"/32\\\": \\\"\\\"\", ((last==FNR)?\"\n\t}\n\":\",\")}" $SOURCE | \
#			tee -a "$OUTPUT"

#jq '.prefixes[] | [.ip_prefix, .service] | @tsv' < aws-ipranges.txt | \
#	sed -e 's/\\t/": "/' > /tmp/p
#
#jq '.prefixes[] | [.ip_prefix, .region] | @tsv' < aws-ipranges.txt | \
#	sed -e 's/\\t/": "/' >> /tmp/p
#

