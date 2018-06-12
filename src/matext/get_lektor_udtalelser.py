#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python -*-
import json
import logging
import os
from fetch_fields import get_lektor
from corepo_harvester.fetch_commondata import fetch_commondata_content


logger = logging.getLogger(__name__)


def fetch_lektor_udtalelse(path, outdir='lektor_udtalelser', limit=None):

    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    shards = [os.environ['COREPO_SHARD0_URL'], os.environ['COREPO_SHARD1_URL']]

    pids = []
    with open(path) as fh:
        pids = [line.strip() for line in fh]
    if limit:
        pids = pids[:limit]

    for shard in shards:
        result = fetch_commondata_content(shard, pids, parser_function=get_lektor)
        for pid, text in result:
            with open(os.path.join(outdir, pid + '.json'), 'w') as fh:
                fh.write(json.dumps(text) + '\n')


def cli():
    """ Commandline interface """
    import argparse

    parser = argparse.ArgumentParser(description='høst lektor_udtalelser')
    parser.add_argument('pidfile',
                        help='File with pids forslagsbeskrivelse pids')
    parser.add_argument('-l', '--limit', dest='limit', type=int,
                        help='limit number og harvested items)', default=None)
    parser.add_argument('-o', '--outdir', dest='outdir',
                        help='folder to dump reviews in. default is \'lektor_udtalelser\'', default='lektor_udtalelser')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='verbose output')
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
    fetch_lektor_udtalelse(args.pidfile, outdir=args.outdir, limit=args.limit)


if __name__ == '__main__':
    cli()
