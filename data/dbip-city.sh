#!/bin/bash
#
# Download DB-IP's free City Lite database (updated monthly).
#   https://db-ip.com/db/lite.php
# License: CC BY 4.0 - attribution required:
#   "IP geolocation data by DB-IP (https://db-ip.com)". Coincidentally this is
#   also freely redistributable, unlike MaxMind's GeoLite2-City.
# Loaded automatically by data/ip2asn_lookup.py, e.g. from the root:
#   ./data/dbip-city.sh

MONTH="$(date +%Y-%m)"

# The current month usually exists by a few days in; fall back to last
# month's release otherwise.
for TRY in "$MONTH" "$(date -d '1 month ago' +%Y-%m)"; do
	SOURCE="dbip-city-lite-${TRY}.mmdb"
	URL="https://download.db-ip.com/free/dbip-city-lite-${TRY}.mmdb.gz"

	# Already fetched? (this month's copy only, so a rerun gets the new month)
	if [ -s "${SOURCE}.gz" ] && [ "$TRY" = "$MONTH" ]; then
		echo "Already downloaded: ${SOURCE}.gz - delete it to refetch."
		exit 0
	fi

	if wget -q -O "${SOURCE}.gz" "$URL"; then
		# Save size/date of source file, like the other data files do
		ls -l "${SOURCE}.gz" > "${SOURCE}.gz.txt"

		# ip2asn_lookup.py decompresses on first use too, but be helpful now
		gzip -dkf "${SOURCE}.gz"

		echo "Downloaded ${SOURCE}.gz ($(du -h "${SOURCE}.gz" | cut -f1) packed, \
$(du -h "$SOURCE" | cut -f1) unpacked)"
		exit 0
	fi

	echo "Not found: $URL"
	rm -f "${SOURCE}.gz"
done

echo "Could not download DB-IP City Lite. Check https://db-ip.com/db/lite.php" >&2
exit 1
