#!/bin/bash

# Grab 2 networks from each file and ping them twice on their .1 IP

for i in *-ctd-data.json; do
	shuf $i | \
		egrep '\.0/' | \
		cut -f 2 -d'"' | \
		grep -P '^\d+\.' | \
		head -2 | \
		perl -p -e 's#\.\d+/\d+#.1#'
done | \
	shuf | \
	xargs -n 1 | \
		while read host; do
			ping -c 2 $host
			nc -v -w 3 -z $host 80
		done
