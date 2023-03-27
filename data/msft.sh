#!/bin/bash

. ~/scripts/generic-linux-funcs.sh

# Should end with -ctd-data.json
OUTPUT=04-msft-ctd-data.json
SOURCE=msft-ipranges.txt
URL="https://www.microsoft.com/en-us/download/confirmation.aspx?id=53602"
URL="https://download.microsoft.com/download/B/2/A/B2AB28E1-DAE1-44E8-A867-4987FE089EBE/msft-public-ips.csv"

#wget -O "$SOURCE" "$URL"
MAX_CACHE_AGE=$((7*24*60))
download_if_not_older "$SOURCE" "$MAX_CACHE_AGE" "$URL"

TEMPFILE="/tmp/msft-parse.XXX"

grep '/' "$SOURCE" | \
	cut -f 1 -d, > "$TEMPFILE"

echo -e '\t"MSFT": [' > "$OUTPUT"
awk 'BEGIN{
	while( (getline t < ARGV[1]) > 0)last++;close(ARGV[1])}
	{print "\t[\"" $0 "\", \"\"]", ((last==FNR) ? "\n\t]\n" :",")}' "$TEMPFILE" \
	| cat >> "$OUTPUT"

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
#	sed -e 's/\\t/": "/' > /tmp/p
#
#jq '.prefixes[] | [.ip_prefix, .region] | @tsv' < aws-ipranges.txt | \
#	sed -e 's/\\t/": "/' >> /tmp/p
#

