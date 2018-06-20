#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python -*-
import joblib
import json
import numpy as np
import pkg_resources as pr
import re
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity
from matext.d2v.parse_taxonomy import parse_taxonomy, parse_tags
from matext.d2v.maps import LitteraturSidenMapper
from matext.d2v.modelbuilder import FILTERS
import gensim.parsing.preprocessing as pre
from colored import fg, bg, attr


def load_model(path):
    data = joblib.load(path)
    return data['model'], data['frequencies'], data['vocabulary']


def infer_taxonomy_vectors(model, taxonomy_path=None):
    labels = []
    M = []
    for nid, entry in parse_taxonomy().items():
        _, word = entry.rsplit('::', 1)
        if word in model.wv:
            labels.append(entry)
            M.append(model.wv[word])
    return np.array(M), labels


def tokenizer(text):
    for token in list(set([re.sub(r'([^\s\w]|_)+', '', token).strip() for token in text.split()])):
        yield token

MAPPER = LitteraturSidenMapper()

def find_nearest_words(model, work):
    # tags = parse_tags()
    # tax = parse_taxonomy()
    # ids = tags[work]['ids']
    # ts = [tax[d] for d in ids if 'stemning' in tax[d]]
    
    text = MAPPER.get_text(work)
    # print(text)
    # print(ts)
    
    M, labels = infer_taxonomy_vectors(model, taxonomy_path=None)
    max_dists = defaultdict(lambda: 0)

    for token in pre.preprocess_string(text, filters=FILTERS):
        if token in model.wv:
            v = model.wv[token].reshape(1, -1)
            dists = cosine_similarity(M, v)
            am = np.argmax(dists)
            max_dists[labels[am]] = max(max_dists[labels[am]], np.max(dists))

    md = sorted([(k, d) for k, d in max_dists.items()], key=lambda x: x[1])
    i = 0
    rtags = []
    for k, v in md:
        if i > 10:
            break
        if 'stemning::' in k and v > 0.5:
            i += 1

            rtags.append(k)
            # print(k, v)
    return rtags


def __load_pmap(path):
    with open(path) as fh:
        return json.load(fh)


def eval_model(model_path, pidmap_path, mapper):
    model, _, _ = load_model(model_path)
    pmap = __load_pmap(pidmap_path)
    tax = parse_taxonomy()
    tags = parse_tags()
    common = 0
    preds = 0
    for work in pmap['dev']:
        ids = sorted([tax[d] for d in tags[work]['ids'] if 'stemning' in tax[d]])
        text = mapper.get_text(work)
        tag_list = sorted(find_nearest_words(model, work))
        
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


    # md = sorted([(k, v) for k, v in max_dists.items()], key=lambda x: x[1])
    # for k, v in md:
    #     print(k, v)
                
    
    # print(sorted([(k, v) for k, v in max_dists.items()], key=lambda x: x[1], reverse=True))
                # print(k, d)
            # dists = sorted(zip(labels, [d[0] for d in dists]), key=lambda x: x[1])
            # for dist in dists:
            #     print(dist)
            


    
            # title = re.sub(r'([^\s\w]|_)+', '', params['title']).strip()  # self.pattern.sub('', params['title'])




#     model, frequencies, vocabulary = load_model(model_path)

if __name__ == '__main__':
    model_path = '/home/shm/models/dk-word-embeddings/model-300-332618646.pkl'
    eval_model(model_path, pr.resource_filename('matext', 'data/litteratursiden_pidmap.json'), MAPPER)

    
    

    # model, _, _ = load_model(model_path)
    # find_nearest_words(model, 'work:24576112')
    # find_nearest_words(None, 'work:24576112')
    
