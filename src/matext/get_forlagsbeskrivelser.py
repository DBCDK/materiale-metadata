#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python -*-
import logging
import os
from fetch_fields import get_forlagsbeskrivelse
from corepo_harvester.fetch_commondata import fetch_commondata_content


logger = logging.getLogger(__name__)


def fetch_forlagsbeskrivelse(path, outdir='forlagsbeskrivelser', limit=None):

    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    shards = [os.environ['COREPO_SHARD0_URL'], os.environ['COREPO_SHARD1_URL']]

    pids = []
    with open(path) as fh:
        pids = [line.strip() for line in fh]
    if limit:
        pids = pids[:limit]

    for shard in shards:
        result = fetch_commondata_content(shard, pids, parser_function=get_forlagsbeskrivelse)
        for pid, text in result:
            with open(os.path.join(outdir, pid + '.txt'), 'w') as fh:
                fh.write(text + '\n')


def cli():
    """ Commandline interface """
    import argparse

    parser = argparse.ArgumentParser(description='høst forlagsbeskrivelser')
    parser.add_argument('pidfile',
                        help='File with pids forslagsbeskrivelse pids')
    parser.add_argument('-l', '--limit', dest='limit', type=int,
                        help='limit number og harvested items)', default=None)
    parser.add_argument('-o', '--outdir', dest='outdir',
                        help='folder to dump reviews in. default is \'forlagsbeskrivelser\'', default='forlagsbeskrivelser')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='verbose output')
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
    fetch_forlagsbeskrivelse(args.pidfile, outdir=args.outdir, limit=args.limit)


if __name__ == '__main__':
    cli()
