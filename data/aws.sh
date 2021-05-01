#!/bin/bash

OUTPUT=03-aws-ctd-data.json
SOURCE=aws-ipranges.txt

#wget -O "$SOURCE" https://ip-ranges.amazonaws.com/ip-ranges.json

echo -e '\t"AWS": {' | tee "$OUTPUT"
#awk "BEGIN{
#	while( (getline t < ARGV[1]) > 0)last++;close(ARGV[1])}
#		{print \"\t\\\"\" \$0 \"/32\\\": \\\"\\\"\", ((last==FNR)?\"\n\t}\n\":\",\")}" $SOURCE | \
#			tee -a "$OUTPUT"

jq '.prefixes[] | [.ip_prefix, .service] | @tsv' < aws-ipranges.txt | \
	sed -e 's/\\t/": "/' > /tmp/p

jq '.prefixes[] | [.ip_prefix, .region] | @tsv' < aws-ipranges.txt | \
	sed -e 's/\\t/": "/' >> /tmp/p

	awk "BEGIN{
		while( (getline t < ARGV[1]) > 0)last++;close(ARGV[1])}
		{print \"\t\" \$0, ((last==FNR)?\"\n\t}\n\":\",\")}" /tmp/p | \
			tee -a "$OUTPUT"

