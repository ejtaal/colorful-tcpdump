#!/bin/bash

. ~/scripts/generic-linux-funcs.sh

OUTPUT=03-aws-ctd-data.json
SOURCE=aws-ipranges.txt
URL="https://ip-ranges.amazonaws.com/ip-ranges.json"

TEMPFILE="/tmp/aws-parse.XXX"

#wget -O "$SOURCE" https://ip-ranges.amazonaws.com/ip-ranges.json
MAX_CACHE_AGE=$((7*24*60))
download_if_not_older "$SOURCE" "$MAX_CACHE_AGE" "$URL"

echo -e '\t"AWS": [' > "$OUTPUT"
#awk "BEGIN{
#	while( (getline t < ARGV[1]) > 0)last++;close(ARGV[1])}
#		{print \"\t\\\"\" \$0 \"/32\\\": \\\"\\\"\", ((last==FNR)?\"\n\t}\n\":\",\")}" $SOURCE | \
#			tee -a "$OUTPUT"

jq '.prefixes[] | [.ip_prefix, .service] | @tsv' < aws-ipranges.txt | \
	sed -e 's/\\t/", "/' > "$TEMPFILE"

jq '.prefixes[] | [.ip_prefix, .region] | @tsv' < aws-ipranges.txt | \
	sed -e 's/\\t/", "/' >> "$TEMPFILE"

	awk "BEGIN{
		while( (getline t < ARGV[1]) > 0)last++;close(ARGV[1])}
		{print \"\t[\" \$0 \"]\", ((last==FNR)?\"\n\t]\n\":\",\")}" "$TEMPFILE" \
		| cat >> "$OUTPUT"

rm -f "$TEMPFILE"
