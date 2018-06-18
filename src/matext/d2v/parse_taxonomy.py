#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python -*-
import json
import os
import pkg_resources as pr
from psycopg2 import connect
import psycopg2.extras


class Cursor():
    """ postgres cursor """
    def __init__(self, postgres_url):
        self.postgres_url = postgres_url

    def __enter__(self):

        self.conn = connect(self.postgres_url)
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return self.cur

    def __exit__(self, type, value, traceback):
        self.cur.close()
        self.conn.close()


def parse_taxonomy(path=None):
    if not path:
        path = pr.resource_filename('matext', 'data/taxonomy.json')

    with open(path) as fh:
        data = json.load(fh)

        keys_ = {}

        def keys(tree, path=''):

            if type(tree) == dict:
                for key, value in tree.items():
                    keys(value, path + '::' + key)
            else:
                for e in tree:
                    key = path[2:] + '::' + e['title']
                    keys_[e['id']] = key
    keys(data)
    return keys_


def get_pid2work(pids, db_url=None):
    if not db_url:
        db_url = os.environ['LOWELL_URL']
    p2w = {}
    with Cursor(db_url) as cur:
        stmt = "SELECT pid, workid FROM relations WHERE pid IN %(pids)s"
        cur.execute(stmt, {'pids': tuple(pids)})
        for row in cur:
            p2w[row['pid']] = row['workid']
    return p2w


def parse_tags(path=None, db_url=None):
    if not path:
        path = pr.resource_filename('matext', 'data/exportTags.json')

    data = None
    with open(path) as fh:
        data = json.load(fh)
    pids = [e['pid'] for e in data]
    p2w = get_pid2work(pids, db_url)

    tags = {}
    for entry in data:
        workid = p2w[entry['pid']]
        tags[workid] = {'pid': entry['pid'],
                        'ids': [e['id'] for e in entry['selected']]}
    return tags
