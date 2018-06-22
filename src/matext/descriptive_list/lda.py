#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python -*-
import joblib
import json
import numpy as np
import os
import pkg_resources as pr
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.pipeline import Pipeline
import gensim.parsing.preprocessing as pre
from colored import fg, bg, attr
from matext.d2v.modelbuilder import FILTERS
from matext.d2v.maps import LitteraturSidenMapper
from matext.d2v.parse_taxonomy import Cursor
from gensim.models.ldamodel import LdaModel
from gensim.models.lsimodel import LsiModel
from gensim import corpora


def stopwords():
    with open(pr.resource_filename('matext', 'data/stopord.txt')) as fh:
        return [w.strip() for w in fh.readlines()]


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


def train(outfile=None, limit=None):
    sw = stopwords()
    texts = [t for t in get_texts(limit=limit)]
    labels, texts = zip(*texts)
    texts = [pre.preprocess_string(text, filters=FILTERS) for text in texts]
    texts = [[w for w in t if w not in sw] for t in texts]
    dictionary = corpora.Dictionary(texts)
    dictionary.filter_extremes(no_below=20, no_above=0.1)
    corpus = [dictionary.doc2bow(text) for text in texts]
    lda = LdaModel(corpus, id2word=dictionary, num_topics=10)
    lsi = LsiModel(corpus, id2word=dictionary, num_topics=10)
    return lda, lsi

# if __name__ == '__main__':
#     train(limit=100)
