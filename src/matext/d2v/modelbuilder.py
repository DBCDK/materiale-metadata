#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python -*-
import json
import pkg_resources as pr
from gensim.models.doc2vec import TaggedDocument
from gensim.models.doc2vec import Doc2Vec
import gensim.parsing.preprocessing as pre
import joblib

from maps import LektorMapper, LitteraturSidenMapper, ForlagsBeskrivelseMapper


FILTERS = [pre.strip_tags, pre.strip_punctuation, pre.strip_multiple_whitespaces, pre.strip_numeric, pre.strip_short]


def docs(mapfile, mapper):
    data = None
    with open(mapfile) as fh:
        data = json.load(fh)['train']
    for work in data:
        text = mapper.get_text(work)
        tokens = pre.preprocess_string(text, filters=FILTERS)
        yield TaggedDocument(tokens, [work])


def train(doc_iter, outfile_prefix=None, size=300, dm=1, epochs=100):
    d = [x for x in doc_iter]
    model = Doc2Vec(size=size, dm=dm, min_count=2)
    model.build_vocab(d)
    model.train(d, total_examples=model.corpus_count, epochs=epochs)
    if outfile_prefix:
        outfile = outfile_prefix + "_%d.d2v" % size
        joblib.dump(model, outfile)
    return model

if __name__ == '__main__':
    mapper = LitteraturSidenMapper()
    mapfile = pr.resource_filename('matext', 'data/litteratursiden_pidmap.json')
    train(docs(mapfile, mapper), outfile_prefix='litteratursiden')

    mapper = LektorMapper()
    mapfile = pr.resource_filename('matext', 'data/lektor_pidmap.json')
    train(docs(mapfile, mapper), outfile_prefix='lektor')

    mapper = ForlagsBeskrivelseMapper()
    mapfile = pr.resource_filename('matext', 'data/forlagsbeskrivelser_pidmap.json')
    train(docs(mapfile, mapper), outfile_prefix='forlagsbeskrivelser')
