#!/bin/bash

OUTPUT=02-tor-ctd-data.json
SOURCE=tor-exits.txt

#wget -O "$SOURCE" https://check.torproject.org/torbulkexitlist

echo -e '\t"TOREXIT": [' | tee "$OUTPUT"
awk "BEGIN{
	while( (getline t < ARGV[1]) > 0)last++;close(ARGV[1])}
		{print \"\t[\\\"\" \$0 \"/32\\\", \\\"\\\"]\", ((last==FNR)?\"\n\t]\n\":\",\")}" $SOURCE | \
			tee -a "$OUTPUT"

#sed -e "s/^/\t'/" -e "s/$/': '',"
