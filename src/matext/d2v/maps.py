#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python -*-
import json
import os
from random import shuffle
from parse_taxonomy import get_pid2work, parse_tags


class ForlagsBeskrivelseMapper():

    def __init__(self, folder=None):
        self.folder = folder
        if not folder:
            self.folder = folder = '/home/shm/git/matext/forlagsbeskrivelser'

        self.pid2file = {}
        self.pids = []
        for f in os.listdir(self.folder):
            pid, _ = f.split('.', 1)
            self.pid2file[pid] = f
            self.pids.append(pid)
        pid2work = get_pid2work(self.pids)
        self.work2pid = {v: k for k, v in pid2work.items()}
        self.work2file = {w: self.pid2file[p] for w, p in self.work2pid.items()}

    def get_text(self, work):
        path = self.work2file[work]
        with open(os.path.join(self.folder, path)) as fh:
            return fh.read()

    def write_map(self, dev_frac=0.1, outfile='forlagsbeskrivelser_pidmap.json'):
        work2tags = parse_tags()

        kompas_works = [w for w in work2tags if w in self.work2pid]
        corpus = [w for w in self.work2pid if w not in work2tags]

        shuffle(kompas_works)
        ix = int(len(kompas_works) * dev_frac)

        data = {'train': kompas_works[ix:],
                'dev': kompas_works[:ix],
                'corpus': corpus}
        print('train', len(data['train']))
        print('dev', len(data['dev']))
        print('corpus', len(data['corpus']))
        with open(outfile, 'w') as fh:
            json.dump(data, fh)


class LektorMapper():

    def __init__(self, folder=None):
        self.folder = folder
        if not folder:
            self.folder = folder = '/home/shm/git/matext/lektor_udtalelser'

        self.pid2file = {}
        self.pids = []
        for f in os.listdir(self.folder):

            with open(os.path.join(self.folder, f)) as fh:
                data = json.load(fh)
                if 'Beskrivelse' in data:
                    pid, _ = f.split('.', 1)
                    self.pid2file[pid] = f
                    self.pids.append(pid)
        pid2work = get_pid2work(self.pids)
        self.work2pid = {v: k for k, v in pid2work.items()}
        self.work2file = {w: self.pid2file[p] for w, p in self.work2pid.items()}

    def get_text(self, work):
        path = self.work2file[work]
        with open(os.path.join(self.folder, path)) as fh:
            data = json.load(fh)
            return data['Beskrivelse']

    def write_map(self, dev_frac=0.1, outfile='lektor_pidmap.json'):
        work2tags = parse_tags()

        kompas_works = [w for w in work2tags if w in self.work2pid]
        corpus = [w for w in self.work2pid if w not in work2tags]

        shuffle(kompas_works)
        ix = int(len(kompas_works) * dev_frac)

        data = {'train': kompas_works[ix:],
                'dev': kompas_works[:ix],
                'corpus': corpus}
        print('train', len(data['train']))
        print('dev', len(data['dev']))
        print('corpus', len(data['corpus']))
        with open(outfile, 'w') as fh:
            json.dump(data, fh)


class LitteraturSidenMapper():

    def __init__(self, folder=None):
        self.folder = folder
        if not folder:
            self.folder = folder = '/home/shm/git/matext/litteratursiden_reviews'

        self.pid2file = {}
        self.pids = []
        for f in os.listdir(self.folder):
            pid, _ = f.split('_', 1)
            self.pid2file[pid] = f
            self.pids.append(pid)
        pid2work = get_pid2work(self.pids)
        self.work2pid = {v: k for k, v in pid2work.items()}
        self.work2file = {w: self.pid2file[p] for w, p in self.work2pid.items()}

    def get_text(self, work):
        path = self.work2file[work]
        with open(os.path.join(self.folder, path)) as fh:
            return fh.read()

    def write_map(self, dev_frac=0.1, outfile='litteratursiden_pidmap.json'):
        work2tags = parse_tags()

        kompas_works = [w for w in work2tags if w in self.work2pid]
        corpus = [w for w in self.work2pid if w not in work2tags]

        shuffle(kompas_works)
        ix = int(len(kompas_works) * dev_frac)

        data = {'train': kompas_works[ix:],
                'dev': kompas_works[:ix],
                'corpus': corpus}
        with open(outfile, 'w') as fh:
            json.dump(data, fh)


# if __name__ == '__main__':
#     # m = LitteraturSidenMapper()
#     m = ForlagsBeskrivelseMapper()
#     # m = LektorMapper()
#     m.write_map()
