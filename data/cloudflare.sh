#!/bin/bash


. ~/scripts/generic-linux-funcs.sh

OUTPUT=01-cloudflare-ctd-data.json
MAX_CACHE_AGE=$((7*24*60))

SOURCE=cf-ips-v4.txt
URL="https://www.cloudflare.com/ips-v4"
#wget -O cf-ips-v4.txt https://www.cloudflare.com/ips-v4
# Careful, this doesn't work through Tor as CF will throw up captcha's etc...
download_if_not_older "$SOURCE" "$MAX_CACHE_AGE" "$URL"

SOURCE=cf-ips-v6.txt
URL="https://www.cloudflare.com/ips-v6"

#wget -O cf-ips-v6.txt https://www.cloudflare.com/ips-v6
download_if_not_older "$SOURCE" "$MAX_CACHE_AGE" "$URL"


TEMPFILE="/tmp/cf-parse.XXX"

cat cf-ips-v?.txt > "$TEMPFILE"

echo -e '\t"CF": [' | tee "$OUTPUT"
awk "BEGIN{
	while( (getline t < ARGV[1]) > 0)last++;close(ARGV[1])}
		{print \"\t[\\\"\" \$0 \"\\\", \\\"\\\"]\", ((last==FNR)?\"\n\t]\n\":\",\")}" "$TEMPFILE" | \
			tee -a "$OUTPUT"

#sed -e "s/^/\t'/" -e "s/$/': '',"
