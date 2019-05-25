#! /usr/bin/env bash

DIR=$(pwd)
echo $DIR

#zip_codes="02142 02141 02140 02139 02138 02134 02115 02199"
#zip_codes="02142 02141 02140 02139 02138 02135"
zip_codes="02135"
#zip_codes="02139 02138" # Cambridge
#zip_codes="02445 02446 02447 02467" # Brookline


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

download() {
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

download brighton 02135
download cambridge 02138 02139
