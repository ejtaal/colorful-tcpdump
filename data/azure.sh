#!/bin/bash

. ~/scripts/generic-linux-funcs.sh

check_json_syntax() {
	local filename="$1"
	if ! which jq > /dev/null; then
		echo "jq not installed, please fix."
		exit 1
	fi
	if jq . < "$filename" > /dev/null; then
		return 0
	fi
	return 1

}

# Should end with -ctd-data.json
# This is one massive convoluted json mess, so can go at the back of
# the queue for lookups
OUTPUT=99-azure-ctd-data.json
SOURCE=azure-ipranges.txt
#URL="https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519"
##URL="https://download.microsoft.com/download/7/1/D/71D86715-5596-4529-9B13-DA13A5DE5B63/ServiceTags_Public_20210426.json"
## Needs manual update every time?!? Microsoft come on!
#URL="https://download.microsoft.com/download/7/1/D/71D86715-5596-4529-9B13-DA13A5DE5B63/ServiceTags_Public_20230320.json"


#wget -O "$SOURCE" "$URL"
#download_if_not_older "$SOURCE" "$MAX_CACHE_AGE" "$URL"
#
#SOURCE=azure-ipranges-auto.txt
#TEMPSOURCE="/tmp/azure-parse-auto.XXX"
## Alternative way:
#URL='https://management.azure.com/subscriptions/subId/providers/Microsoft.Network/locations/westcentralus/serviceTags?api-version=2022-09-01'
#
#download_if_not_older "$TEMPSOURCE" "$MAX_CACHE_AGE" "$URL"

TEMPSOURCE="/tmp/azure-parse-auto.XXX"
TEMPFILE="/tmp/azure-parse.XXX"

parse_azure() {
	tag="$1"
	file="$2"

	
	# TODO: Normalize this horrendous mess of json data
	jq '.values[].properties | . as $line | .addressPrefixes[] as $a | [$a, $line.systemService] | @tsv' < "$file" | \
		sed -e 's/\\tAzure/\\t/' -e 's/\\t/", "/' | \
		sort -uV | \
		cat > "$TEMPFILE"
		#tr -d '"' | \
	
	jq '.values[].properties | . as $line | .addressPrefixes[] as $a | [$a, $line.region] | @tsv' < "$file" | \
		sed -e 's/\\tAzure/\\t/' -e 's/\\t/", "/' | \
		sort -uV | \
		cat >> "$TEMPFILE"
	
	if [ -s "$OUTPUT" ]; then
		echo ',' >> "$OUTPUT"
	fi

	echo -e "\t\"$tag\": [" | cat >> "$OUTPUT"
	awk 'BEGIN{
		while( (getline t < ARGV[1]) > 0)last++;close(ARGV[1])}
		{print "\t[" $0 "]", ((last==FNR) ? "\n\t]\n" :",")}' "$TEMPFILE" | \
			cat >> "$OUTPUT"

}


MAX_CACHE_AGE=$((7*24*60))
file_tags="AZ-DE AzureGermany.json
AZ-GOV AzureGovernment.json
AZ-CN China.json
AZ-PUB Public.json"

> "$OUTPUT"

echo "$file_tags" \
| while read tag filename; do
	echo filename = $filename
	# Courtesy of the kind soul at https://twitter.com/derdanu
	URL="https://azureipranges.azurewebsites.net/Data/${filename}"
	SOURCE="$tag.json"

	download_if_not_older "$SOURCE" "$MAX_CACHE_AGE" "$URL"
	if check_json_syntax "$SOURCE"; then
		parse_azure "$tag" "$SOURCE"
	fi
done

ls -l "$OUTPUT"
head -3 "$OUTPUT"
echo ...
tail -3 "$OUTPUT"
rm -f "$TEMPFILE"
exit 0





#
#
#TEMPFILE="/tmp/azure-parse.XXX"
#
## TODO: Normalize this horrendous mess of json data
#jq '.values[].properties | . as $line | .addressPrefixes[] as $a | [$a, $line.systemService] | @tsv' < azure-ipranges.txt | \
#	sed -e 's/\\tAzure/\\t/' -e 's/\\t/", "/' | \
#	sort -uV | \
#	cat > "$TEMPFILE"
#	#tr -d '"' | \
#
#jq '.values[].properties | . as $line | .addressPrefixes[] as $a | [$a, $line.region] | @tsv' < azure-ipranges.txt | \
#	sed -e 's/\\tAzure/\\t/' -e 's/\\t/", "/' | \
#	sort -uV | \
#	cat >> "$TEMPFILE"
#
#echo -e '\t"AZURE": [' | cat > "$OUTPUT"
#awk 'BEGIN{
#	while( (getline t < ARGV[1]) > 0)last++;close(ARGV[1])}
#	{print "\t[" $0 "]", ((last==FNR) ? "\n\t]\n" :",")}' "$TEMPFILE" | \
#		cat >> "$OUTPUT"
#
#
#
#ls -l "$OUTPUT"
#head -3 "$OUTPUT"
#echo ...
#tail -3 "$OUTPUT"
#rm -f "$TEMPFILE"

#awk "BEGIN{
#	while( (getline t < ARGV[1]) > 0)last++;close(ARGV[1])}
#		{print \"\t\\\"\" \$0 \"/32\\\": \\\"\\\"\", ((last==FNR)?\"\n\t}\n\":\",\")}" $SOURCE | \
#			cat >> "$OUTPUT"

#jq '.prefixes[] | [.ip_prefix, .service] | @tsv' < aws-ipranges.txt | \
#	sed -e 's/\\t/": "/' > "$TEMPFILE"
#
#jq '.prefixes[] | [.ip_prefix, .region] | @tsv' < aws-ipranges.txt | \
#	sed -e 's/\\t/": "/' >> "$TEMPFILE"
#

