#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python -*-
import joblib
import json
import os
from collections import Counter
import gensim.parsing.preprocessing as pre
import pkg_resources as pr

from colored import fg, bg, attr

from modelbuilder import FILTERS
from parse_taxonomy import parse_taxonomy, parse_tags
from maps import LektorMapper, LitteraturSidenMapper, ForlagsBeskrivelseMapper


class Model():

    def __init__(self, model):
        self.model = model
        if type(model) == str and os.path.isfile(model):
            self.model = joblib.load(model)
            self.tax = parse_taxonomy()
            self.tags = parse_tags()

    def _similar_works(self, text, top_n=10):
        tokens = pre.preprocess_string(text, filters=FILTERS)
        v = self.model.infer_vector(tokens)
        return self.model.docvecs.most_similar(positive=[v], topn=top_n)

    def __call__(self, text, top_n_works=10, tag_max=10, tag_min_occur=2):
        works = self._similar_works(text, top_n_works)
        counter = Counter()
        for w, val in works:
            for t in self.tags[w]['ids']:
                counter[t] += 1
        tag_list = []
        for i, (tag, count) in enumerate(counter.most_common()):
            if count <= tag_min_occur or len(tag_list) > tag_max:
                break
            if 'stemning' in self.tax[tag]:
                tag_list.append((self.tax[tag], count))
        return tag_list


def __load_pmap(path):
    with open(path) as fh:
        return json.load(fh)


def eval_model(model_path, pidmap_path, mapper):
    model = Model(model_path)
    pmap = __load_pmap(pidmap_path)
    tax = parse_taxonomy()
    tags = parse_tags()
    common = 0
    preds = 0
    for work in pmap['dev']:
        ids = sorted([tax[d] for d in tags[work]['ids'] if 'stemning' in tax[d]])
        text = mapper.get_text(work)
        tag_list = sorted([t for t,_ in model(text, top_n_works=7, tag_min_occur=1)])
        preds += len(tag_list)
        print('%s %s %s' % (attr('bold'), work, attr('reset')))
        print(text)
        inter = set(ids) & set(tag_list)
        common += len(inter)
        diff1 = set(ids) - set(tag_list)
        diff2 = set(tag_list) - set(ids)
        print('fælles   %s %s %s' % (fg('green'), inter, attr('reset')))
        print('i kompas %s %s %s' % (fg('red'), diff1, attr('reset')))
        print('i model  %s %s %s' % (fg('blue'), diff2, attr('reset')))
        print()
        print()
    print('num common %d/%s' % (common, preds))
    
if __name__ == '__main__':

    eval_model(pr.resource_filename('matext', 'data/litteratursiden_300.d2v'),
               pr.resource_filename('matext', 'data/litteratursiden_pidmap.json'),
               LitteraturSidenMapper('/home/shm/git/matext/litteratursiden_reviews'))

    
    
