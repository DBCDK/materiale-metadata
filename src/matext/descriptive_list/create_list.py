#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python -*-
import joblib
import os
import gensim.parsing.preprocessing as pre
import pkg_resources as pr
from colored import fg, bg, attr

from matext.d2v.modelbuilder import FILTERS
from matext.d2v.parse_taxonomy import Cursor


class CreateList():

    def __init__(self, model=None):
        self.model = model
        if not model:
            self.model = joblib.load(pr.resource_filename('matext', 'data/litteratursiden_300.d2v'))
        self.db = os.environ['LOWELL_URL']

    def __call__(self, text, topn=10, cutoff=0.4):
        tokens = pre.preprocess_string(text, filters=FILTERS)
        # tokens *= 1
        vec = self.model.infer_vector(tokens, steps=20, alpha=0.025)
        sims_org = [(w, v) for w, v in self.model.docvecs.most_similar(positive=[vec], topn=100) if v >= cutoff]
        sims = [w for w, v in sims_org][:topn]
        vals = [v for w, v in sims_org][:topn]

        if sims:
            inf = {}
            with Cursor(self.db) as cur:
                cur.execute("SELECT * FROM workid_meta WHERE workid IN %(works)s", {'works': tuple(sims)})
                for row in cur:
                    inf[row['workid']] = "%s %s" % (row['creator'].ljust(30), row['title'])

        print("\nDescription: %s%s%s\n" % (attr('bold'), text, attr('reset')))
        for sim, val in zip(sims, vals):
            print("  " + sim.ljust(20) + inf[sim] + "%f" % val)


def cli():

    import argparse
    parser = argparse.ArgumentParser(description='create descroption list')
    parser.add_argument('description')

    args = parser.parse_args()

    creator = CreateList()
    creator(args.description)

if __name__ == '__main__':
    cli()
