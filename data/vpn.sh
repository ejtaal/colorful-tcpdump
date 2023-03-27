#!/bin/bash

. ~/scripts/generic-linux-funcs.sh

# Should end with -ctd-data.json
OUTPUT=10-vpn-ctd-data.json
SOURCE=vpn-ipranges.txt
URL="https://api.mullvad.net/www/relays/all/"

#wget -O "$SOURCE" "$URL"
MAX_CACHE_AGE=$((7*24*60))
download_if_not_older "$SOURCE" "$MAX_CACHE_AGE" "$URL"

TEMPFILE="/tmp/vpn-parse.XXX"

> "$TEMPFILE"

jq '.[] | [.ipv4_addr_in,.city_code] | @tsv' < "$SOURCE" | \
	sed -e 's/\\t/", "/' | \
	cat >> "$TEMPFILE"

jq '.[] | [.ipv6_addr_in,.city_code] | @tsv' < "$SOURCE" | \
	sed -e 's/\\t/", "/' | \
	fgrep -v '"",' | \
	cat >> "$TEMPFILE"

echo -e '\t"MULLVAD": [' > "$OUTPUT"
awk 'BEGIN{
	while( (getline t < ARGV[1]) > 0)last++;close(ARGV[1])}
	{print "\t[" $0 "]", ((last==FNR) ? "\n\t]\n" :",")}' "$TEMPFILE" | \
		cat >> "$OUTPUT"

ls -l "$OUTPUT"
head -3 "$OUTPUT"
echo ...
tail -3 "$OUTPUT"
rm -f "$TEMPFILE"
#awk "BEGIN{
#	while( (getline t < ARGV[1]) > 0)last++;close(ARGV[1])}
#		{print \"\t\\\"\" \$0 \"/32\\\": \\\"\\\"\", ((last==FNR)?\"\n\t}\n\":\",\")}" $SOURCE | \
#			tee -a "$OUTPUT"

#jq '.prefixes[] | [.ip_prefix, .service] | @tsv' < aws-ipranges.txt | \
#	sed -e 's/\\t/": "/' > "$TEMPFILE"
#
#jq '.prefixes[] | [.ip_prefix, .region] | @tsv' < aws-ipranges.txt | \
#	sed -e 's/\\t/": "/' >> "$TEMPFILE"
#

