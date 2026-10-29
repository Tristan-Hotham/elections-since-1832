"""Shared paths and loaders for the elections-since-1832 study."""
import gzip, json, re, unicodedata
import pandas as pd

DATA_IN = '/home/claude/hist/_data18/elections-since-1832/'
ROOT = '/home/claude/hist/elections-since-1832/'
OUT = ROOT + 'data/'
WORK = ROOT + 'work/'


def tsv(t):
    L = t.strip('\n').split('\n')
    h = [x.lstrip('?') for x in L[0].split('\t')]
    return pd.DataFrame([dict(zip(h, l.split('\t'))) for l in L[1:]])


def lab(s):
    if not isinstance(s, str):
        return s
    m = re.match(r'^"(.*)"(@en|\^\^.*)?$', s)
    return m.group(1) if m else s


def load_wikidata():
    B = json.load(gzip.open(DATA_IN + 'elec1832_wikidata_v1.json.gz'))
    m = tsv(B['q']['members'])
    d = tsv(B['q']['districts'])
    for c in ['geL', 'personL', 'pgL']:
        m[c] = m[c].map(lab)
    for c in ['dL', 'dDesc', 'adminL']:
        d[c] = d[c].map(lab)
    m['gek'] = m['geL'].str.replace(' United Kingdom general election', '', regex=False)
    return m, d


def load_parliament():
    df = pd.read_csv(DATA_IN + 'ukge_1832_2019_download.csv.gz', header=None,
                     names=['gen', 'year', 'start', 'end', 'con', 'party', 'cand', 'unc', 'votes', 'turnout'])
    df['gek'] = df['gen'].str.replace(' General Election', '', regex=False)
    return df


def load_hoc():
    return json.load(gzip.open(DATA_IN + 'elec1832_hoc2010_2024_v1.json.gz'))


def norm(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()
    s = s.replace('&', ' and ').replace("'", '')
    s = re.sub(r'[^a-z ]', ' ', s)
    return s


ELECTIONS = ['1832', '1835', '1837', '1841', '1847', '1852', '1857', '1859', '1865', '1868', '1874', '1880',
             '1885', '1886', '1892', '1895', '1900', '1906', 'January 1910', 'December 1910', '1918', '1922',
             '1923', '1924', '1929', '1931', '1935', '1945', '1950', '1951', '1955', '1959', '1964', '1966',
             '1970', 'February 1974', 'October 1974', '1979', '1983', '1987', '1992', '1997', '2001', '2005',
             '2010', '2015', '2017', '2019', '2024']
