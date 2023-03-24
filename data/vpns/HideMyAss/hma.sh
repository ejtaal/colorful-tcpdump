#!/bin/bash

# wget -O hma-countries.html https://www.hidemyass.com/en-gb/servers
# wget -O hma-countries.json https://slc.ff.avast.com/v1/locationList/hide_my_ass

jq -j '.locationList[] as $a | $a.locationDetails.countryId,",",$a.locationDetails.countryName,",",$a.locationType,",",$a.locationDetails.cityName,",",$a.ipsCount,"\n"' \
	< hma-countries.json \
	| cat > hma-countries-report.txt

grep VIRTUAL hma-countries-report.txt \
	| cut -f 1 -d , | sort -u \
	| cat > hma-virtual-countries.txt
grep PHYSICAL hma-countries-report.txt \
	| cut -f 1 -d , | sort -u \
	| cat > hma-physical-countries.txt

