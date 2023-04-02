#!/bin/bash

wget -O index.html 'https://nordvpn.com/servers/'

cat index.html \
| perl -pe 's/(<tr class="ServersTable__row)/\n$1/g' \
| fgrep 'tr class="ServersTable__row' \
| perl -pe 's/.*?class="Text mr-2 text-underline">//' \
| perl -pe 's/<.*?>/ /g' \
| cat > nordvpn-countries.txt
