#!/bin/bash

FINAL_OUTPUT=ctd-data.json

echo "$@"
echo "$#"
	
echo "{" | tee "$FINAL_OUTPUT"

i=0
for f in "$@"; do
	i=$((i+1))
	echo "$i: $f ..."
	cat "$f" | tee -a "$FINAL_OUTPUT"
	if [ "$i" != "$#" ]; then
		echo -e "\t," | tee -a "$FINAL_OUTPUT"
	fi
done
echo "}" | tee -a "$FINAL_OUTPUT"
