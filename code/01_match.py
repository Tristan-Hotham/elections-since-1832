"""Match each constituency contest in the Parliament 1832 to 2019 file to its Wikidata district.

Exact label match first; the rest are matched within the same election by name tokens and by
the overlap between candidate surnames (Parliament file) and the surnames of the members
Wikidata records as elected for that district at that election. Writes work/match.csv.
"""
import collections, difflib, re, sys
import pandas as pd
sys.path.insert(0, '/home/claude/hist/elections-since-1832/code')
from common import *

m, d = load_wikidata()
dl = d.drop_duplicates('d').set_index('d')['dL']
m['dL'] = m['d'].map(dl)
df = load_parliament()

STOP = {'and', 'the', 'of', 'boroughs', 'borough', 'district', 'burghs', 'county', 'division', 'city', 'upon', 'on', 'cities', 'parliamentary', 'constituency'}
SYN = {'caernarvon': 'caernarfon', 'carnarvon': 'caernarfon', 'carnarvonshire': 'caernarvonshire', 'radnor': 'radnorshire', 'argyll': 'argyllshire',
       'dumfries': 'dumfriesshire', 'north': 'n', 'northern': 'n', 'south': 's', 'southern': 's', 'east': 'e', 'eastern': 'e',
       'west': 'w', 'western': 'w', 'central': 'c', 'mid': 'c', 'middle': 'c'}


def toks(s):
    return {SYN.get(t, t) for t in norm(s).split() if t not in STOP}


def surn(name):  # Parliament file: "Surname, Forename"
    return norm(name.split(',')[0]).split()[-1] if isinstance(name, str) and name.strip() else ''


def wsurn(label):
    if not isinstance(label, str):
        return ''
    w = norm(re.sub(r',.*$', '', re.sub(r'\(.*?\)', '', label))).split()
    return w[-1] if w else ''


rows = []
for g, sub in df.groupby('gek'):
    wm = m[m.gek == g]
    wd_names = wm.groupby('d')['dL'].first()
    wd_sur = wm.groupby('d')['personL'].apply(lambda s: {wsurn(x) for x in s})
    by_label = collections.defaultdict(list)
    for q, l in wd_names.items():
        by_label[l].append(q)
    used = set()
    pending = []
    for c, cs in sub.groupby('con'):
        if c in by_label and len(by_label[c]) == 1:
            rows.append((g, c, by_label[c][0], 'exact', 1.0))
            used.add(by_label[c][0])
        else:
            pending.append((c, {surn(x) for x in cs.cand}))
    cand = [q for q in wd_names.index if q not in used]
    scores = []
    for c, cs in pending:
        tc = toks(c)
        for q in cand:
            tq = toks(wd_names[q])
            jac = len(tc & tq) / max(1, len(tc | tq))
            seq = difflib.SequenceMatcher(None, norm(c), norm(wd_names[q])).ratio()
            sur = len(cs & wd_sur[q]) / max(1, len(wd_sur[q]))
            s = 0.45 * max(jac, seq) + 0.55 * sur
            scores.append((s, c, q, jac, seq, sur))
    scores.sort(reverse=True)
    done_c = set()
    for s, c, q, jac, seq, sur in scores:
        if c in done_c or q in used:
            continue
        if s < 0.45:
            continue
        rows.append((g, c, q, 'fuzzy:%.2f/%.2f/%.2f' % (jac, seq, sur), round(s, 3)))
        done_c.add(c); used.add(q)
    for c, cs in pending:
        if c not in done_c:
            rows.append((g, c, '', 'unmatched', 0))
out = pd.DataFrame(rows, columns=['gek', 'con', 'd', 'how', 'score'])
out['dL'] = out['d'].map(dl)
out.to_csv(WORK + 'match.csv', index=False)
print(out.how.str.split(':').str[0].value_counts())
f = out[out.how != 'exact']
print(f[f.score < 0.7].drop_duplicates(['con', 'dL']).to_string())
print(out[out.how == 'unmatched'].to_string())
