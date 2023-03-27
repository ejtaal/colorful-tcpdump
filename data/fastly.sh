#!/bin/bash

. ~/scripts/generic-linux-funcs.sh

# Should end with -ctd-data.json
OUTPUT=20-fastly-ctd-data.json
SOURCE=fastly-ipranges.txt
URL="https://api.fastly.com/public-ip-list"

MAX_CACHE_AGE=$((7*24*60))
download_if_not_older "$SOURCE" "$MAX_CACHE_AGE" "$URL"

TEMPFILE="/tmp/fastly-parse.XXX"

ls -l "$SOURCE"
jq ".addresses[], .ipv6_addresses[]" < "$SOURCE" | \
	sed -e 's/$/, ""/' | \
	cat > "$TEMPFILE"
	
awk_fy() {
	name="$1"
	in_file="$2"
	out_file="$3"
	
	echo -e "\t\"$name\": [" > "$out_file"
	awk 'BEGIN{
		while( (getline t < ARGV[1]) > 0)last++;close(ARGV[1])}
		{print "\t[" $0 "]", ((last==FNR) ? "\n\t]\n" :",")}' "$in_file" | \
			cat >> "$out_file"
}


awk_fy FASTLY "$TEMPFILE" "$OUTPUT"

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

#grep '/' "$SOURCE" | \
#	cut -f 1 -d, > "$TEMPFILE"
#
#jq '.[] | [.ipv4_addr_in,.city_code] | @tsv' < "$SOURCE" | \
#	sed -e 's/\\t/": "/' | \
#	tee -a "$TEMPFILE"
#
#jq '.[] | [.ipv6_addr_in,.city_code] | @tsv' < "$SOURCE" | \
#	sed -e 's/\\t/": "/' | \
#	fgrep -v '"":' | \
#	tee -a "$TEMPFILE"
