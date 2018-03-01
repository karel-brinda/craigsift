#! /usr/bin/env python3

import argparse
import itertools
import os
import re
import sys

re_post=re.compile(r'(<li class="result-row".*?/li>)+')

#re_price=re.compile(r'<span class="result-price">\$(\d+)</span>')
re_price=re.compile(r'\$([0-9]+)')
re_link=re.compile(r'<a href="(.*?)"')
re_datetime=re.compile(r'datetime="(.*?)"')
re_desc=re.compile(r'hdrlnk">(.*?)</a')


# remove
# - "available "

out_phrases=[
	'studio',
	'BR available',
	'room available',
	'BR in',
	'BD in',
	'room in',
	'BRs in',
	'BDs in',
	'rooms in',
	'roommate',
	'shared',
	'roommate',
	'flatmate',
	'share',
]


def remove_duplicates(items):
	seen=set()
	items2=[]
	for item in items:
		if not item['url'] in seen:
			items2.append(item)
		seen.add(item['url'])
	return items2


def process_list(list_fn):
	fn=os.path.basename(list_fn).replace(".html","")
	with open(list_fn) as f:
		cont=f.read()
	cont_oneline=cont.replace("\n", " ")
	ms=re_post.findall(cont_oneline)
	#print(ms)

	pr_items=[]

	for it in ms:
		#print(m)
		d=process_item(it)
		d["file"]=fn
		pr_items.append(d)

	pr_items_cat=assign_categories(pr_items)

	return pr_items_cat


def assign_categories(items):
	"""
	categories:
	- ok - probably relevant
	- spam - spam
	- out - out of interest
	- cat - wrong category of advertisement
	"""
	items_cat=[]

	for item in items:
		cat='ok'

		desc_norm=item['desc'].replace("&amp;","")
		for f in out_phrases:
			if desc_norm.lower().find(f)!=-1:
				cat='out'

		if desc_norm==desc_norm.upper():
			cat='spam'

		if desc_norm.find("**")!=-1:
			cat='spam'

		#if item['url'].find("/gbs/abo/")==-1:
		#	cat='cat'

		item['cat']=cat
		items_cat.append(item)

	return items_cat


def process_item(it):
	d={}

	m=re_price.search(it)
	try:
		d["price"]=int(m.group(1))
	except (IndexError, AttributeError):
		d["price"]="NA"

	m=re_link.search(it)
	try:
		d["url"]=m.group(1)
		#d["url"]="https://boston.craigslist.org"+m.group(1)
	except (IndexError, AttributeError):
		d["url"]="NA"

	m=re_datetime.search(it)
	try:
		d["datetime"]=m.group(1)
	except (IndexError, AttributeError):
		d["datetime"]="NA"

	m=re_desc.search(it)
	try:
		d["desc"]=m.group(1)
	except (IndexError, AttributeError):
		d["desc"]="NA"

	return d


def print_as_html(rs):
	print("""
	<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Craigslist filtered results</title>
</head>

<body>
<table>
{}
</table>
</body>

</html>
	""".format(
			"\n".join(
					['<tr><td>{}</td><td>{}</td><td>${}</td><td><a href="{}">{}</a></td><td>{}</td></tr>'.format(r['datetime'], r['cat'], r['price'], r['url'], r['desc'], r['file']) for r in rs]
				)
		)
	)

def main():
	parser = argparse.ArgumentParser(description="")

	parser.add_argument('-c',
			metavar='str',
			dest='cat',
			help='category (ok / spam / cat / out)',
			default=None,
		)

	parser.add_argument('ls',
			metavar='str',
			help='',
			nargs='+',
		)

	args = parser.parse_args()

	rs=itertools.chain(*[process_list(l) for l in args.ls])
	rs=remove_duplicates(rs)
	rs.sort(key=lambda x: x['datetime'], reverse=True)

	if args.cat is None:
		print_as_html(rs)
	else:
		print_as_html(filter(lambda x: x['cat']==args.cat, rs))

	#for x in r:
	#	if x['cat']=="ok":
	#		print(x)


if __name__ == "__main__":
	main()
