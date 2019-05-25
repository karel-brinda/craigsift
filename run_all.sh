#! /usr/bin/env bash

DIR=$(pwd)

set -e
set -o pipefail

download_zip() {
	zip="$1"
	(
	cd lists
	echo "Downloading $zip"
	printf '' > $zip.html
	for s in `seq 0 120 600`; do
		curl "https://boston.craigslist.org/search/nfa?s=$s&min_bedrooms=$minBedrooms&search_distance=0&postal=$zip&min_price=$minPrice&max_price=$maxPrice" >> "$zip.html"
	done
	)
}

sift() {
	mkdir -p "$1"
	cd "$1"
	mkdir -p lists
	shift

	for zip in $@; do
		download_zip "$zip"
	done

	$DIR/process_list.py ./lists/* > results.all.html
	$DIR/process_list.py -c ok ./lists/* > results.ok.html && (open results.ok.html || true)
}

minBedrooms=2
minPrice=1900
maxPrice=2500

sift brighton 02135
sift cambridge 02138 02139
sift cambridge-ext 02142 02141 02140 02139 02138 02143
sift brookline 02445 02446 02447 02467

