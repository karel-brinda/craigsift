#! /usr/bin/env python3

import argparse
import itertools
import os
import re
import sys

re_post = re.compile(r'(<li class="result-row".*?/li>)+')

#re_price=re.compile(r'<span class="result-price">\$(\d+)</span>')
re_price = re.compile(r'\$([0-9]+)')
re_link = re.compile(r'<a href="(.*?)"')
re_datetime = re.compile(r'datetime="(.*?)"')
re_desc = re.compile(r'hdrlnk">(.*?)</a')

# remove
# - "available "

re_out_phrases0 = [
    r'studio',
    #r'BR available',
    r'room available',
    r'available room',
    #r'BR in',
    r'BD in',
    #r'1 BD',
    #r'1 BR',
    #r'1 bed',
    #r'1BD',
    #r'1BR',
    #r'1bed',
    r'sept',
    r'9/1',
    #r'6/1',
    #r'room in',
    #r'BRs in',
    r'BDs in',
    #r'rooms in',
    r'roommate',
    r'shared',
    r'sharing',
    r'roommate',
    r'flatmate',
    r'share',
    #r'Huron',
    r'\[?(6|7)/1\]?\s*\*?NO FEE\*?',
    r'(luxury|stylish|peaceful|superb|desirable|well-loved|cats? ok)',
]

re_spam_phrases0 = [
    r'\s\S\s\S\s\S\s\S\s',
    r'\*\*',
]

re_whitelist0 = [
    r'deleaded',
    r'8/1',
    r'aug',
]

re_out_phrases = [re.compile(r'.*' + x + r'.*', re.IGNORECASE) for x in re_out_phrases0]
re_spam_phrases = [re.compile(r'.*' + x + r'.*', re.IGNORECASE) for x in re_spam_phrases0]
re_whitelist = [re.compile(r'.*' + x + r'.*', re.IGNORECASE) for x in re_whitelist0]


def remove_duplicates(items):
    seen = set()
    items2 = []
    for item in items:
        if not item['url'] in seen:
            items2.append(item)
        seen.add(item['url'])
    return items2


def process_list(list_fn):
    fn = os.path.basename(list_fn).replace(".html", "")
    with open(list_fn) as f:
        cont = f.read()
    cont_oneline = cont.replace("\n", " ")
    ms = re_post.findall(cont_oneline)
    #print(ms)

    pr_items = []

    for it in ms:
        #print(m)
        d = process_item(it)
        d["file"] = fn
        pr_items.append(d)

    pr_items_cat = assign_categories(pr_items)

    return pr_items_cat


def assign_categories(items):
    """
    categories:
    - ok - probably relevant
    - spam - spam
    - out - out of interest
    - cat - wrong category of advertisement
    """
    items_cat = []

    for item in items:
        cat = 'ok'

        filt=""

        desc_norm = item['desc'].replace("&amp;", "")
        for r in re_out_phrases:
            m = r.match(desc_norm)
            if m:
                cat = 'out'
                filt=r
                break

        uppers=sum(1 for c in desc_norm if c.isupper())
        lowers=sum(1 for c in desc_norm if c.islower())

        if uppers > 0.5*(uppers+lowers):
            cat = 'spam'

        for r in re_spam_phrases:
            m = r.match(desc_norm)
            if m:
                filt=r
                cat = 'spam'
                break

        for r in re_whitelist:
            m = r.match(desc_norm)
            if m:
                filt=r
                cat = 'ok'
                break


        #if item['url'].find("/gbs/abo/")==-1:
        #   cat='cat'

        item['cat'] = cat
        item['filtered']=filt
        items_cat.append(item)

    return items_cat


def process_item(it):
    d = {}

    m = re_price.search(it)
    try:
        d["price"] = int(m.group(1))
    except (IndexError, AttributeError):
        d["price"] = "NA"

    m = re_link.search(it)
    try:
        d["url"] = m.group(1)
        #d["url"]="https://boston.craigslist.org"+m.group(1)
    except (IndexError, AttributeError):
        d["url"] = "NA"

    m = re_datetime.search(it)
    try:
        d["datetime"] = m.group(1)
    except (IndexError, AttributeError):
        d["datetime"] = "NA"

    m = re_desc.search(it)
    try:
        d["desc"] = m.group(1)
    except (IndexError, AttributeError):
        d["desc"] = "NA"

    return d


def remove_duplicates(rs):
    filtered = []
    seen = set()
    for r in rs:
        if not r["desc"] in seen:
            filtered.append(r)
            seen.add(r["desc"])
    return filtered


def print_as_html(rs):
    print("""
    <!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Craigslist filtered results</title>
<style>
          a:link              {{ color:black; }}
          a:visited           {{ color:#aaa; }}
</style>
</head>

<body>
<table>
{}
</table>
</body>

</html>
    """.format("\n".join([
        '<tr title="{}""><td>{}</td><td>{}</td><td>${}</td><td><a href="{}">{}</a></td><td>{}</td></tr>'
        .format(r['filtered'], r['datetime'], r['cat'], r['price'], r['url'], r['desc'],
                r['file']) for r in rs
    ])))


def main():
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        '-c',
        metavar='str',
        dest='cat',
        help='category (ok / spam / cat / out)',
        default=None,
    )

    parser.add_argument(
        'ls',
        metavar='str',
        help='',
        nargs='+',
    )

    args = parser.parse_args()

    rs = itertools.chain(*[process_list(l) for l in args.ls])
    rs = remove_duplicates(rs)
    rs.sort(key=lambda x: x['datetime'], reverse=True)

    rs = remove_duplicates(rs)

    if args.cat is None:
        print_as_html(rs)
    else:
        print_as_html(filter(lambda x: x['cat'] == args.cat, rs))

    #for x in r:
    #   if x['cat']=="ok":
    #       print(x)


if __name__ == "__main__":
    main()
