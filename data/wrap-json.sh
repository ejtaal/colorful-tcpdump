#!/bin/bash

FINAL_OUTPUT=ctd-data.json

ctd_data_files=(*-ctd-data.json)

# Filter out files that are not tag data sources:
# - ctd-data.json: this script's own previous merged output
# - ip2asn-ctd-data.json: pure ASN data (whole routing table), loaded
#   separately by colorful-tcpdump.py via data/ip2asn_lookup.py.
#   Merging it here would dump every ASN range into the radix tree,
#   duplicating labels the lookup already provides.
filtered=()
for f in ${ctd_data_files[*]}; do
	case "$f" in
		ctd-data.json|ip2asn-ctd-data.json)
			echo "skipping: $f (not a tag data source)"
			;;
		*)
			filtered+=("$f")
			;;
	esac
done
ctd_data_files=(${filtered[*]})

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

