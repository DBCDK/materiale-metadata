#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python -*-
from collections import defaultdict
import json
import os
import requests
from tqdm import tqdm
from matext.d2v.parse_taxonomy import parse_taxonomy, parse_tags, Cursor


def get_recs(pids):

    url = 'http://recomole.mcp1-proxy.dbc.dk/recomole/loan-cosim'
    r = requests.post(url, data=json.dumps({'like': pids, 'limit': 20}))
    if not r.ok:
        r.raise_for_status()

    return [e['pid'] for e in r.json()['response']]


def get_meta(pid):
    with Cursor(os.environ['LOWELL_URL']) as cur:
        cur.execute("SELECT metadata FROM metadata WHERE pid=%(pid)s", {'pid': pid})
        rep = pid.ljust(30)
        for row in cur:
            m = row['metadata']
            rep += m.get('creator', [''])[0].ljust(30)
            rep += m.get('title', [''])[0].ljust(30)
            rep += '\n' + m.get('abstract', [''])[0]
        return rep
 

def main():
    tax = parse_taxonomy()
    tax = {k: v for k, v in tax.items() if 'stemning::' in v}

    work2pid = {}
    tag2pids = defaultdict(list)
    tags = parse_tags()

    pid2tags = defaultdict(list)

    for work, data in tags.items():
        work2pid[work] = data['pid']
        for id_ in [i for i in data['ids'] if i in tax]:
            tag2pids[id_].append(data['pid'])

    tag2pids = {k: v for k, v in tag2pids.items() if len(v) >= 3}
    for tag, pids in tqdm(tag2pids.items(), ncols=100):
        for rec_pid in get_recs(pids):
            pid2tags[rec_pid].append(tag)

    pid2tags = {k: v for k, v in pid2tags.items() if len(v) >= 3}
    for pid, tags in pid2tags.items():
        print(get_meta(pid))
        for tag in tags:
            print("  * " + tax[tag])
        print()


    print(len(pid2tags))

if __name__ == '__main__':
    main()

    # print(get_meta('870970-basis:09332251'))
