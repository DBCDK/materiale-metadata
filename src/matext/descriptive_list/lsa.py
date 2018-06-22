#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python -*-
import joblib
import json
import numpy as np
import os
import pkg_resources as pr
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.pipeline import Pipeline
import gensim.parsing.preprocessing as pre
from colored import fg, bg, attr
from matext.d2v.modelbuilder import FILTERS
from matext.d2v.maps import LitteraturSidenMapper
from matext.d2v.parse_taxonomy import Cursor


def get_texts(mapper=None, mapfile=None, limit=None):
    if not mapper:
        mapper = LitteraturSidenMapper('/home/shm/git/matext/litteratursiden_reviews')
    if not mapfile:
        mapfile = pr.resource_filename('matext', 'data/litteratursiden_pidmap.json')
    works = []
    with open(mapfile) as fh:
        data = json.load(fh)
        works = data['train'] + data['dev'] + data['corpus']
    for i, work in enumerate(works):
        if limit and i >= limit:
            break
        yield work, mapper.get_text(work)


def stopwords():
    with open(pr.resource_filename('matext', 'data/stopord.txt')) as fh:
        return [w.strip() for w in fh.readlines()]


def train(mapper=None, mapfile=None, outfile=None, limit=None):

    texts = [t for t in get_texts(limit=limit)]
    labels, texts = zip(*texts)
    labels = np.array(labels)
    vectorizer = TfidfVectorizer(stop_words=stopwords(),
                                 use_idf=True,
                                 smooth_idf=True)

    svd_model = TruncatedSVD(n_components=100,
                             algorithm='randomized',
                             n_iter=10)

    svd_transformer = Pipeline([('tfidf', vectorizer),
                                ('svd', svd_model)])

    svd_matrix = svd_transformer.fit_transform(texts)

    if outfile:
        joblib.dump({'vectorizer': vectorizer,
                     'model': svd_model,
                     'M': svd_matrix,
                     'labels': labels}, outfile,)

    return vectorizer, svd_model, svd_matrix, labels


def get_recs(pids, limit=10):

    url = 'http://recomole.mcp1-proxy.dbc.dk/recomole/loan-cosim'
    r = requests.post(url, data=json.dumps({'like': pids, 'limit': limit, 'filters': {'authorFlood': 1}}))
    if not r.ok:
        r.raise_for_status()
    return r.json()['response']


class CreateList():

    def __init__(self, model=None):
        if not model:
            model = joblib.load(pr.resource_filename('matext', 'data/litteratursiden_lsa.pkl'))

        self.vectorizer = model['vectorizer']
        self.model = model['model']
        self.M = model['M']
        self.labels = model['labels']

        self.mapper = LitteraturSidenMapper('/home/shm/git/matext/litteratursiden_reviews')  # only used to map works to pids in recommend
        self.db = os.environ['LOWELL_URL']

    def __call__(self, text, topn=6, cutoff=None):

        tokens = pre.preprocess_string(text, filters=FILTERS)
        v = self.vectorizer.transform(tokens)
        v_ = self.model.transform(v)
        sums = np.sum(self.M.dot(v_.T), axis=1)
        so = np.argsort(sums)
        sims = {k: 'L' for k in list(self.labels[so][-topn:][::-1])}
        recs = self.__recommend(sims, topn)
        sims.update(recs)
        self.__print(text, sims)

    def __recommend(self, works, limit):
        pids = [self.mapper.work2pid[w] for w in list(works.keys())[:5]]
        works = [e['debug-work'] for e in get_recs(pids, limit)]
        return {k: 'R' for k in works}

    def __print(self, text, sims):
        if sims:
            inf = {}
            with Cursor(self.db) as cur:
                cur.execute("SELECT * FROM workid_meta WHERE workid IN %(works)s", {'works': tuple(sims.keys())})
                for row in cur:
                    creator = row['creator'] if row['creator'] else ''
                    title = row['title'] if row['title'] else ''
                    inf[row['workid']] = "%s %s" % (creator.ljust(30), title)

        print("\nDescription: %s%s%s\n" % (attr('bold'), text, attr('reset')))
        for sim, type_ in sims.items():
            work = "%s" % sim.ljust(20)
            if type_ == 'R':
                work = "%s%s%s" % (fg('blue'), sim.ljust(20), attr('reset'))
            print("  " + work + inf[sim])
        print()


def cli():

    import argparse
    parser = argparse.ArgumentParser(description='create descroption list')
    parser.add_argument('description')
    parser.add_argument('-l', '--limit', help='limits number of presented items', type=int, default=10)
    
    args = parser.parse_args()

    creator = CreateList()
    creator(args.description, topn=args.limit)

if __name__ == '__main__':
    cli()
    # train(outfile='litteratursiden_lsa.pkl')
