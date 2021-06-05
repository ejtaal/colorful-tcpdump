#!/bin/bash

FINAL_OUTPUT=ctd-data.json

ctd_data_files=(*-ctd-data.json)
echo "$@"
echo "$#"
#${#ctd_data_files[*]}
	
echo "{" | tee "$FINAL_OUTPUT"

i=0
for f in ${ctd_data_files[*]}; do
	i=$((i+1))
	echo "$i: $f ..."
	{
		echo "{"
		cat  "$f"
		echo "}"
	} | if ! cat | jq . > /dev/null; then
		echo "SYNTAX ERROR in $f ... aborting."
		exit 1
	fi
	cat "$f" | tee -a "$FINAL_OUTPUT"
	if [ "$i" != "${#ctd_data_files[*]}" ]; then
		echo -e "\t," | tee -a "$FINAL_OUTPUT"
	fi
done
echo "}" | tee -a "$FINAL_OUTPUT"

# Syntax check it:
echo "Output file:"
ls -l "$FINAL_OUTPUT"

echo -n "Syntax check ..."
jq . < "$FINAL_OUTPUT" > /dev/null && echo OK

