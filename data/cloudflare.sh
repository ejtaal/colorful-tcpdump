#!/bin/bash

OUTPUT=01-cloudflare-ctd-data.json

#wget -O cf-ips-v4.txt https://www.cloudflare.com/ips-v4
#wget -O cf-ips-v6.txt https://www.cloudflare.com/ips-v6

cat cf-ips-v?.txt > /tmp/p

echo -e '\t"CF": {' | tee "$OUTPUT"
awk "BEGIN{
	while( (getline t < ARGV[1]) > 0)last++;close(ARGV[1])}
		{print \"\t\\\"\" \$0 \"\\\": \\\"\\\"\", ((last==FNR)?\"\n\t}\n\":\",\")}" /tmp/p | \
			tee -a "$OUTPUT"

#sed -e "s/^/\t'/" -e "s/$/': '',"
