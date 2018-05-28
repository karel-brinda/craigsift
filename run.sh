#! /usr/bin/env bash

DIR=$(dirname $0)

zip_codes="02447"

set -e
set -o pipefail

rm -fr lists
mkdir lists
(
	cd lists
	for zip in $zip_codes; do
		echo "Downloading $zip"
		curl "https://boston.craigslist.org/search/nfa?search_distance=0&postal=$zip&min_price=1400&max_price=2100&fake-param=$(date +%s)" > "$zip.html" &
	done;
	wait
)

${DIR}/process_list.py ./lists/* > results.all.html
${DIR}/process_list.py -c ok ./lists/* > results.ok.html && (open results.ok.html || true)

