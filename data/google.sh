#!/bin/bash

# Should end with -ctd-data.json
OUTPUT=07-google-ctd-data.json
SOURCE=google-ipranges.txt
URL="https://www.gstatic.com/ipranges/goog.json"

wget -O "$SOURCE" "$URL"

grep '/' "$SOURCE" | \
	awk '{ print $2 ", \"\"" }' | \
	sort -uV | \
	tee /tmp/p

echo -e '\t"GOOG": [' | tee "$OUTPUT"
awk 'BEGIN{
	while( (getline t < ARGV[1]) > 0)last++;close(ARGV[1])}
	{print "\t[" $0 "]", ((last==FNR) ? "\n\t]\n" :",")}' /tmp/p | \
		tee -a "$OUTPUT"

#jq '.values[].properties | . as $line | .addressPrefixes[] as $a | [$a, $line.systemService] | @tsv' < azure-ipranges.txt | \
#	sed -e 's/\\tAzure/\\t/' -e 's/\\t/": "/' | \
#	sort -uV | \
#	tee /tmp/p
#	#tr -d '"' | \
#
#jq '.values[].properties | . as $line | .addressPrefixes[] as $a | [$a, $line.region] | @tsv' < azure-ipranges.txt | \
#	sed -e 's/\\tAzure/\\t/' -e 's/\\t/": "/' | \
#	sort -uV | \
#	tee -a /tmp/p
#
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

