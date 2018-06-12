#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python -*-
import logging
from lxml import etree


""" Namespacemap for commonData xml"""
NSMAP = {'ting': 'http://www.dbc.dk/ting',
         'dkabm': 'http://biblstandard.dk/abm/namespace/dkabm/',
         'ac': 'http://biblstandard.dk/ac/namespace/',
         'dkdcplus': 'http://biblstandard.dk/abm/namespace/dkdcplus/',
         'oss': 'http://oss.dbc.dk/ns/osstypes',
         'dc': 'http://purl.org/dc/elements/1.1/',
         'dcterms': 'http://purl.org/dc/terms/',
         'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
         'docbook': 'http://docbook.org/ns/docbook',
         'marcx': 'info:lc/xmlns/marcxchange-v1'}


def get_forlagsbeskrivelse(row):
    """ helper function to make parse_commondatas signature conform"""
    return _get_forlagsbeskrivelse(row['content'], pid=row['pid'])


def _get_forlagsbeskrivelse(xml_string, pid=None):
    xml = etree.fromstring(xml_string)

    path = '/ting:container/docbook:article/docbook:section/docbook:para/text()'

    value = xml.xpath(path, namespaces=NSMAP)
    value = value[0] if value else ''
    path = '/ting:container/ting:originalData/DbcWrapper/wroot/wfaust/text()'
    pid = '870970-basis:' + xml.xpath(path, namespaces=NSMAP)[0]

    return (pid, normalize(value))


def get_provider_id(row):
    """ helper function to make parse_commondatas signature conform"""
    return _get_provider_id(row['content'], pid=row['pid'])


def _get_provider_id(xml_string, pid=None):
    xml = etree.fromstring(xml_string)
    path = '/ting:container/marcx:collection/marcx:record/marcx:datafield[@tag="002"]/marcx:subfield[@code="d"]/text()'
    # path = '/ting:container/dkabm:record/dc:identifier[@xsi:type="oss:PROVIDER-ID"]/text()'

    value = xml.xpath(path, namespaces=NSMAP)
    value = value[0] if value else ''
    return (pid, normalize(value))


def _get_lektor(xml_string, pid=None):
    xml = etree.fromstring(xml_string)
    path = '/ting:container/marcx:collection/marcx:record/marcx:datafield[@tag="014"]/marcx:subfield[@code="a"]/text()'
    pid = '870970-basis:' + xml.xpath(path, namespaces=NSMAP)[0]

    path = '/ting:container/docbook:article/docbook:section'
    content = {}
    for node in xml.xpath(path, namespaces=NSMAP):
        tnodes = node.xpath('.//docbook:title/text()', namespaces=NSMAP)
        if tnodes:
            title = tnodes[0]
            text = normalize(node.xpath('.//docbook:para/text()', namespaces=NSMAP)[0])
            content[title] = text
    return (pid, content)


def get_lektor(row):
    """ helper function to make parse_commondatas signature conform"""
    return _get_lektor(row['content'], pid=row['pid'])


def normalize(s):
    """
    normalize string s:
    (1) replace double-a
    (2) strip whitespace around field
    """
    return s.strip().replace('\uA732', 'Aa').replace('\uA733', 'aa')
