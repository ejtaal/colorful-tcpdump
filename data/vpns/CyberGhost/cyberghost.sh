#!/bin/bash

#wget -O cg-countries.txt https://www.cyberghostvpn.com/en_US/vpn-server

egrep '(data-cc=.*data-region=|sat-location_servers)' cg-countries.txt \
	| sed '$!N;s/\n/ /' \
	| perl -pe 's/^.*?data-cc="(.*?)"/\1,/' \
	| perl -pe 's/ data-region="(.*?)">/\1,/' \
	| perl -pe 's/ <div class="sat-location_servers">(.*?)<\/div>/\1/' \
	| cat
