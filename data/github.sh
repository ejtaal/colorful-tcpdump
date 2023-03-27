#!/bin/bash

. ~/scripts/generic-linux-funcs.sh
# Should end with -ctd-data.json
OUTPUT=06-github-ctd-data.json
SOURCE=github-ipranges.txt
URL="https://api.github.com/meta"

MAX_CACHE_AGE=$((7*24*60))
download_if_not_older "$SOURCE" "$MAX_CACHE_AGE" "$URL"

TEMPFILE="/tmp/gh-parse.XXX"

jq 'del(.[] | select(type!="array")) | to_entries | .[] as $line | $line.value[] as $v | [$v, $line.key] | @tsv' < github-ipranges.txt | \
	sed -e 's/\\t/", "/' | \
	sort -uV \
	| grep -v ssh_keys \
	| cat > "$TEMPFILE"

#ls -l "$TEMPFILE"
#exit 1

echo -e '\t"GITHUB": [' > "$OUTPUT"
awk 'BEGIN{
	while( (getline t < ARGV[1]) > 0)last++;close(ARGV[1])}
	{print "\t[" $0 "]", ((last==FNR) ? "\n\t]\n" :",")}' "$TEMPFILE" \
	| cat >> "$OUTPUT"

ls -l "$OUTPUT"
head -3 "$OUTPUT"
echo ...
tail -3 "$OUTPUT"
rm -f "$TEMPFILE"

#jq '.values[].properties | . as $line | .addressPrefixes[] as $a | [$a, $line.systemService] | @tsv' < azure-ipranges.txt | \
#	sed -e 's/\\tAzure/\\t/' -e 's/\\t/": "/' | \
#	sort -uV | \
#	tee "$TEMPFILE"
#	#tr -d '"' | \
#
#jq '.values[].properties | . as $line | .addressPrefixes[] as $a | [$a, $line.region] | @tsv' < azure-ipranges.txt | \
#	sed -e 's/\\tAzure/\\t/' -e 's/\\t/": "/' | \
#	sort -uV | \
#	tee -a "$TEMPFILE"
#
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

