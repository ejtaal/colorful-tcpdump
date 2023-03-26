#!/bin/bash

. ~/scripts/generic-linux-funcs.sh

# Should end with -ctd-data.json
# This is one massive convoluted json mess, so can go at the back of
# the queue for lookups
OUTPUT=91-asn-ctd-data.json
SOURCE=ip2asn-combined.tsv
SOURCE=ip2asn-combined.tsv.gz
URL="https://iptoasn.com/data/ip2asn-combined.tsv.gz"

# wget -O "$SOURCE" "$URL"
MAX_CACHE_AGE=$((7*24*60))
download_if_not_older "$SOURCE" "$MAX_CACHE_AGE" "$URL"

> /tmp/p
zcat "$SOURCE" | \
	grep -i akamai | \
	while read first last stop something country owner; do
		#echo "$first $last $something $country $owner"
		#echo "first = $first, last = $last"
		if echo "$first - $last" | grep -q :; then
			cidr="$(./ipv6_range2cidr.py $first $last)"
		else
			cidr="$(ipcalc -r "$first-$last")"
		fi
		echo "$cidr" | \
			grep -v "^deaggre" | \
			sed -e 's/^/"/' -e 's/$/", ""/' | \
			tee -a /tmp/p
	done


echo -e '\t"AKAMAI": [' | tee "$OUTPUT"
awk 'BEGIN{
	while( (getline t < ARGV[1]) > 0)last++;close(ARGV[1])}
	{print "\t[" $0 "]", ((last==FNR) ? "\n\t]\n" :",")}' /tmp/p | \
		tee -a "$OUTPUT"

# TODO: Now do the same for collections of:
# \tOVH
# \tDREAMHOST
# \t$BIG_TELECOM_COMPANY_FOR_WHICH_IT_IS_COOL_TO_KNOWN_ITS_IP_ADDRESSES?

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

