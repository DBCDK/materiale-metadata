#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python -*-
from d2v.maps import LitteraturSidenMapper, ForlagsBeskrivelseMapper, LektorMapper, AbstractMapper
from d2v.modelbuilder import FILTERS
import matplotlib.pyplot as plt
import gensim.parsing.preprocessing as pre
import pkg_resources as pr
import json
import pandas as pd
import seaborn as sns
plt.switch_backend('agg')

current_palette = sns.color_palette("dark", 10)
sns.palplot(current_palette)


def litsiden():
    f = pr.resource_filename('matext', 'data/litteratursiden_pidmap.json')
    mapper = LitteraturSidenMapper()
    works = []
    df = {}

    lk_frac = None
    with open(f) as fh:
        data = json.load(fh)
        lk_frac = [len(data['train']) + len(data['dev']), len(data['train']) + len(data['dev']) + len(data['corpus'])]
        
        for k in data.keys():
            works += data[k]
    for w in works:
        t = mapper.get_text(w)
        tokens = pre.preprocess_string(t, filters=FILTERS)

        df[w] = [len(tokens), len(t)]

    df = pd.DataFrame.from_dict(df, orient='index')
    df.columns = ['tokens', 'char-length']
    print(df.describe())
    fig, ax = plt.subplots()
    sns.distplot(df['char-length'], ax=ax, bins=100, kde=False, norm_hist=False)
    fig.savefig('lit_hist.png')
    print('LK', lk_frac)


def forlagsbeskrivelser():
    f = pr.resource_filename('matext', 'data/forlagsbeskrivelser_pidmap.json')
    mapper = ForlagsBeskrivelseMapper()
    works = []
    df = {}

    lk_frac = None
    with open(f) as fh:
        data = json.load(fh)
        lk_frac = [len(data['train']) + len(data['dev']), len(data['train']) + len(data['dev']) + len(data['corpus'])]
        
        for k in data.keys():
            works += data[k]
    for w in works:
        try:
            t = mapper.get_text(w)
            tokens = pre.preprocess_string(t, filters=FILTERS)

            df[w] = [len(tokens), len(t)]
        except:
            print("E")

    df = pd.DataFrame.from_dict(df, orient='index')
    df.columns = ['tokens', 'char-length']
    print(df.describe())
    fig, ax = plt.subplots()
    sns.distplot(df['char-length'], ax=ax, bins=100, kde=False, norm_hist=False)
    fig.savefig('forlag_hist.png')
    print('LK', lk_frac)


def lektor_udtalelser():
    f = pr.resource_filename('matext', 'data/lektor_pidmap.json')
    mapper = LektorMapper()
    works = []
    df = {}

    lk_frac = None
    with open(f) as fh:
        data = json.load(fh)
        lk_frac = [len(data['train']) + len(data['dev']), len(data['train']) + len(data['dev']) + len(data['corpus'])]
        
        for k in data.keys():
            works += data[k]
    for w in works:
        try:
            t = mapper.get_text(w)
            tokens = pre.preprocess_string(t, filters=FILTERS)

            df[w] = [len(tokens), len(t)]
        except:
            print("E")

    df = pd.DataFrame.from_dict(df, orient='index')
    df.columns = ['tokens', 'char-length']
    print(df.describe())
    fig, ax = plt.subplots()
    sns.distplot(df['char-length'], ax=ax, bins=100, kde=False, norm_hist=False)
    fig.savefig('lektor_hist.png')
    print('LK', lk_frac)


def notefelt(mapper=None):
    f = pr.resource_filename('matext', 'data/notefelt_pidmap.json')
    if not mapper:
        mapper = AbstractMapper()
    works = []
    df = {}

    lk_frac = None
    with open(f) as fh:
        data = json.load(fh)
        lk_frac = [len(data['train']) + len(data['dev']), len(data['train']) + len(data['dev']) + len(data['corpus'])]
        
        for k in data.keys():
            works += data[k]
    for w in works:
        try:
            t = mapper.get_text(w)
            tokens = pre.preprocess_string(t, filters=FILTERS)

            df[w] = [len(tokens), len(t)]
        except:
            print("E")

    df = pd.DataFrame.from_dict(df, orient='index')
    df.columns = ['tokens', 'char-length']
    print(df.describe())
    fig, ax = plt.subplots()
    sns.distplot(df['char-length'], ax=ax, bins=100, kde=False, norm_hist=False)
    fig.savefig('note_hist.png')
    print('LK', lk_frac)

    
# if __name__ == '__main__':
    # litsiden()
    # forlagsbeskrivelser()
    # lektor_udtalelser()
    # notefelt()
