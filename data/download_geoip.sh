#!/usr/bin/env bash
# download_geoip.sh - Download latest GeoLite2 City database
# This script downloads from a mirror since MaxMind requires account registration
#
# Usage: ./download_geoip.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MMDB_FILE="${SCRIPT_DIR}/GeoLite2-City.mmdb"

echo "Downloading latest GeoLite2 City database..."
echo "(Source: https://github.com/lwpk110/free-geoip-databases)"
echo ""

# Get the latest release version
LATEST_RELEASE=$(curl -sL "https://api.github.com/repos/lwpk110/free-geoip-databases/releases/latest" | grep '"tag_name"' | sed 's/.*"tag_name": "\(.*\)".*/\1/')

if [ -z "$LATEST_RELEASE" ]; then
    echo "Error: Could not determine latest release"
    exit 1
fi

echo "Latest release: $LATEST_RELEASE"

# Download URL
DOWNLOAD_URL="https://github.com/lwpk110/free-geoip-databases/releases/download/${LATEST_RELEASE}/GeoLite2-City-${LATEST_RELEASE}.mmdb"

# Download the city database with retries
MAX_RETRIES=3
RETRY=0
while [ $RETRY -lt $MAX_RETRIES ]; do
    RETRY=$((RETRY + 1))
    if curl -L --retry 2 --retry-delay 3 -o "${MMDB_FILE}" "${DOWNLOAD_URL}" 2>/dev/null; then
        break
    fi
    echo "Attempt $RETRY failed, retrying..."
    sleep 2
done

if [ ! -f "${MMDB_FILE}" ] || [ ! -s "${MMDB_FILE}" ]; then
    echo "Error: Download failed after $MAX_RETRIES attempts"
    echo "Please download manually from:"
    echo "  $DOWNLOAD_URL"
    echo "And save it as: ${MMDB_FILE}"
    exit 1
fi

FILESIZE=$(du -h "${MMDB_FILE}" | cut -f1)
echo ""
echo "Downloaded: ${MMDB_FILE}"
echo "Size: ${FILESIZE}"
echo ""
echo "The database is now ready to use with colorful-tcpdump."
