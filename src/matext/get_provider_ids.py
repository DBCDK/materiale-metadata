#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python -*-
import json
import logging
import os
import sys
from fetch_fields import get_provider_id
from corepo_harvester.fetch_commondata import fetch_commondata_content


logger = logging.getLogger(__name__)


def fetch_provider_ids(path, outfile='ebogs_provider_ids.json', limit=None):

    shards = [os.environ['COREPO_SHARD0_URL'], os.environ['COREPO_SHARD1_URL']]

    pids = []
    with open(path) as fh:
        pids = [line.strip() for line in fh]
    if limit:
        pids = pids[:limit]

    map_ = {}
    for shard in shards:
        result = fetch_commondata_content(shard, pids, parser_function=get_provider_id)
        for pid, provider_id in result:
            if provider_id:
                map_[pid] = provider_id
            # else:
            #     print(pid)
    print('harvested %d ids' % len(map_))
    with open(outfile, 'w') as fh:
        for pid, provider_id in map_.items():
            fh.write(json.dumps({pid: provider_id}) + '\n')


def cli():
    """ Commandline interface """
    import argparse

    parser = argparse.ArgumentParser(description='harvests provider ids')
    parser.add_argument('pidfile',
                        help='File with pids e_bogs pids')
    parser.add_argument('-l', '--limit', dest='limit', type=int,
                        help='limit number og harvested items)', default=None)
    parser.add_argument('-o', '--outfile', dest='outfile',
                        help='file to dump ids in. default is \'ebogs_provider_ids.json\'', default='ebogs_provider_ids.json')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='verbose output')
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
    fetch_provider_ids(args.pidfile, outfile=args.outfile, limit=args.limit)


if __name__ == '__main__':
    cli()
