#!/bin/bash

. ~/scripts/generic-linux-funcs.sh

# Should end with -ctd-data.json
# This is one massive convoluted json mess, so can go at the back of
# the queue for lookups
OUTPUT=99-azure-ctd-data.json
SOURCE=azure-ipranges.txt
URL="https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519"
#URL="https://download.microsoft.com/download/7/1/D/71D86715-5596-4529-9B13-DA13A5DE5B63/ServiceTags_Public_20210426.json"
# Needs manual update every time?
URL="https://download.microsoft.com/download/7/1/D/71D86715-5596-4529-9B13-DA13A5DE5B63/ServiceTags_Public_20230320.json"

#wget -O "$SOURCE" "$URL"
MAX_CACHE_AGE=$((7*24*60))
download_if_not_older "$SOURCE" "$MAX_CACHE_AGE" "$URL"

TEMPFILE="/tmp/azure-parse.XXX"

# TODO: Normalize this horrendous mess of json data
jq '.values[].properties | . as $line | .addressPrefixes[] as $a | [$a, $line.systemService] | @tsv' < azure-ipranges.txt | \
	sed -e 's/\\tAzure/\\t/' -e 's/\\t/", "/' | \
	sort -uV | \
	tee "$TEMPFILE"
	#tr -d '"' | \

jq '.values[].properties | . as $line | .addressPrefixes[] as $a | [$a, $line.region] | @tsv' < azure-ipranges.txt | \
	sed -e 's/\\tAzure/\\t/' -e 's/\\t/", "/' | \
	sort -uV | \
	tee -a "$TEMPFILE"

echo -e '\t"AZURE": [' | tee "$OUTPUT"
awk 'BEGIN{
	while( (getline t < ARGV[1]) > 0)last++;close(ARGV[1])}
	{print "\t[" $0 "]", ((last==FNR) ? "\n\t]\n" :",")}' "$TEMPFILE" | \
		tee -a "$OUTPUT"

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

