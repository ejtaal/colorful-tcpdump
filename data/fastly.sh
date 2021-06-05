#!/bin/bash

# Should end with -ctd-data.json
OUTPUT=20-fastly-ctd-data.json
SOURCE=fastly-ipranges.txt
URL="https://api.fastly.com/public-ip-list"

#wget -O "$SOURCE" "$URL"

ls -l "$SOURCE"
jq ".addresses[], .ipv6_addresses[]" < "$SOURCE" | \
	sed -e 's/$/, ""/' | \
	tee /tmp/p
	



awk_fy() {
	name="$1"
	in_file="$2"
	out_file="$3"
	
	echo -e "\t\"$name\": [" | tee "$out_file"
	awk 'BEGIN{
		while( (getline t < ARGV[1]) > 0)last++;close(ARGV[1])}
		{print "\t[" $0 "]", ((last==FNR) ? "\n\t]\n" :",")}' "$in_file" | \
			tee -a "$out_file"
}


awk_fy FASTLY /tmp/p "$OUTPUT"

ls -l "$OUTPUT"
exit 88

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

#grep '/' "$SOURCE" | \
#	cut -f 1 -d, > /tmp/p
#
#jq '.[] | [.ipv4_addr_in,.city_code] | @tsv' < "$SOURCE" | \
#	sed -e 's/\\t/": "/' | \
#	tee -a /tmp/p
#
#jq '.[] | [.ipv6_addr_in,.city_code] | @tsv' < "$SOURCE" | \
#	sed -e 's/\\t/": "/' | \
#	fgrep -v '"":' | \
#	tee -a /tmp/p
