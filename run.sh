#! /usr/bin/env bash

DIR=$(dirname $0)

#zip_codes="02142 02141 02140 02139 02138 02134 02115 02199"
zip_codes="02142 02141 02140 02139 02138 02135"
#zip_codes="02135"


set -e
set -o pipefail

rm -fr lists
mkdir lists
(
	cd lists
	for zip in $zip_codes; do
		echo "Downloading $zip"
		curl "https://boston.craigslist.org/search/nfa?search_distance=1&postal=$zip&min_price=1700&max_price=2400" > "$zip.html" &
	done;
	wait
)

${DIR}/process_list.py ./lists/* > results.all.html
${DIR}/process_list.py -c ok ./lists/* > results.ok.html && (open results.ok.html || true)

