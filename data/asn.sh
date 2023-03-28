#!/bin/bash

. ~/scripts/generic-linux-funcs.sh

# Should end with -ctd-data.json
# This is one massive convoluted json mess, so can go at the back of
# the queue for lookups
OUTPUT=91-asn-ctd-data.json
FREQ_REPORT=asn-most-common.txt
SOURCE=ip2asn-combined.tsv
SOURCE=ip2asn-combined.tsv.gz
URL="https://iptoasn.com/data/ip2asn-combined.tsv.gz"

# wget -O "$SOURCE" "$URL"
MAX_CACHE_AGE=$((7*24*60))
download_if_not_older "$SOURCE" "$MAX_CACHE_AGE" "$URL"

TEMPFILE="/tmp/asn-parse.XXX"

extract_asn() {
	> "$TEMPFILE"
	tag="$1"
	grep_command="$2"
	hm '*' "Extracting [[ $tag ]] ASN's ..."

		#| pv -l \
#	zcat "$SOURCE" \
#		| grep "$grep_command"
#	exit 1
	zcat "$SOURCE" \
		| grep "$grep_command" \
		| while read first last stop something country owner; do
			#echo "$first $last $something $country $owner"
			#echo "first = $first, last = $last"
			if echo "$first - $last" | grep -q :; then
				cidr="$(./ipv6_range2cidr.py $first $last)"
			else
				cidr="$(ipcalc -r "$first-$last")"
			fi
			echo "$cidr" | \
				grep -v "^deaggre" | \
				sed -e 's/^/"/' -e 's/$/", ""/' \
				| cat >> "$TEMPFILE"
			echo -n '.'
		done
	
	if [ -s "$OUTPUT" ]; then
		echo , >> "$OUTPUT"
	fi

	echo -e "\t\"$tag\": [" >> "$OUTPUT"
	awk 'BEGIN{
		while( (getline t < ARGV[1]) > 0)last++;close(ARGV[1])}
		{print "\t[" $0 "]", ((last==FNR) ? "\n\t]\n" :",")}' "$TEMPFILE" \
		| cat >> "$OUTPUT"
	echo 'done'
}

> "$OUTPUT"

hm '*' "ASN frequency report ..."
zcat ip2asn-combined.tsv.gz \
| cut -f 5- -d "	" \
| sort \
| uniq -c \
| sort -rn \
| cat > "$FREQ_REPORT"

head -20 "$FREQ_REPORT"

extract_asn OVH 'OVH$'
extract_asn ONEWEB "ONEWEB"
extract_asn SPACEX "SPACEX-STARLINK"
extract_asn AKAMAI "AKAMAI"

ls -l "$OUTPUT"
head -3 "$OUTPUT"
echo ...
tail -3 "$OUTPUT"
rm -f "$TEMPFILE"

# TODO: Now do the same for collections of:
# DREAMHOST
# $BIG_TELECOM_COMPANY_FOR_WHICH_IT_IS_COOL_TO_KNOW_ITS_IP_ADDRESSES?
