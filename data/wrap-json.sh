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

# Syntax check it:
echo "Output file:"
ls -l "$FINAL_OUTPUT"

echo -n "Syntax check ..."
jq . < "$FINAL_OUTPUT" > /dev/null && echo OK

