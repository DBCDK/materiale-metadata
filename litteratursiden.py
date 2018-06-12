#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python -*-
"""
Script used to download reviews from literattursiden
"""
import datetime
import joblib
import logging
import os
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
logger = logging.getLogger(__name__)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


def fetch_reviewed_material(solr_url, limit=None, rows=10):
    """
    Retrieve pids of reviewed materail and recordIDs for posts with reviews

    Pids and record are returned as tuples

    """
    fetched = 0
    end = limit
    if not end:
        end = rows + 1

    params = {'q': 'rec.collectionIdentifier:150005-anmeld',
              'start': 0,
              'rows': rows,
              'fl': 'fedoraPid term.reviewedIdentifier rec.bibliographicRecordId'}

    while params['start'] < end:
        r = requests.get(solr_url.rstrip('/') + '/query', params=params)
        if not r.ok:
            r.raise_for_status()
        if not limit:
            end = limit = r.json()['response']['numFound']

        params['start'] += params['rows']

        docs = r.json()['response']['docs']
        for doc in docs:
            if fetched >= end:
                break
            if 'term.reviewedIdentifier' in doc and 'rec.bibliographicRecordId' in doc:
                yield doc['term.reviewedIdentifier'][0], doc['rec.bibliographicRecordId']
                fetched += 1
            else:
                # if 'rec.bibliographicRecordId' not in doc:
                #     logger.warning(doc['fedoraPid'])
                logger.warning("document %s missing fields (fields present=%s)" % (doc['fedoraPid'],
                                                                                   str(list(doc.keys()))))


def dump_reviewed_material(solr_url, outfile='pid2recordid.pkl', limit=None):
    start = datetime.datetime.now()
    pid2recordid = {p: r for p, r in fetch_reviewed_material(solr_url, rows=100, limit=limit)}
    logger.info("Fetched %d records in [%s]", len(pid2recordid), datetime.datetime.now() - start)
    logger.debug("Dumping data to '%s'", outfile)
    joblib.dump(pid2recordid, outfile)


def _scrape_review(html):
    soup = BeautifulSoup(html, 'html.parser')
    article = soup.find('article', attrs={'role': 'article'})
    article = article.find('div', attrs={'class': 'desktop-node-content'})
    article = article.find('div', attrs={'class': 'content'})
    text = article.find('div', attrs={'class': 'field--name-field-review-body'})
    return text.text.strip()


def fetch_review(review_id):
    url = 'https://litteratursiden.dk/node/' + str(review_id)
    r = requests.get(url)
    if not r.ok:
        r.raise_for_status()
    return _scrape_review(r.text)


def scrape_reviews(solr_url, out_dir='reviews', limit=None, rows=100):
    start = datetime.datetime.now()
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    # data = [(p, r) for p, r in fetch_reviewed_material(solr_url, rows=rows, limit=limit)]
    for i, (p, r) in tqdm(enumerate(fetch_reviewed_material(solr_url, rows=rows, limit=limit))):
        path = os.path.join(out_dir, "%s_%s.txt" % (p, r))
        try:
            text = fetch_review(r)
            with open(path, 'w') as fh:
                fh.write(text)
        except Exception as e:
            logger.error("Could not retrive review with id %s" % r)
            logger.error(e)
        if limit and i >= limit:
            break

    logger.info("Fetched all data in [%s]", datetime.datetime.now() - start)



def cli():
    """ Commandline interface """
    import argparse

    # port = 7372

    parser = argparse.ArgumentParser(description='scraping af literattursiden')
    parser.add_argument('-l', '--limit', dest='limit', type=int,
                        help='limits number of harvested reviews)', default=None)
    parser.add_argument('-o', '--outdir', dest='outdir',
                        help='folder to dump reviews in. default is \'reviews\'', default='reviews')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='verbose output')
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
    solr_url = 'http://cisterne-solr.dbc.dk:8984/solr/corepo_20180330_1818_stored/'
    scrape_reviews(solr_url, limit=args.limit, out_dir=args.outdir)

    

if __name__ == '__main__':
    cli()

    
    # solr_url = 'http://cisterne-solr.dbc.dk:8984/solr/corepo_20180330_1818_stored/'
    # scrape_reviews(solr_url, limit=3)
    # review_id = '75413'
    # fetch_review(review_id)


    # dump_reviewed_material(solr_url)
