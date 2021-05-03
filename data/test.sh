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
	xargs -n 1 ping -c 2
