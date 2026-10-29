"""Compare seat totals per party family with the infobox of each English Wikipedia election article.

Infobox party names are mapped to the same families (Conservative includes Liberal Unionists
and allied Unionists where the infobox combines them). Writes work/validate.csv and
work/validate.json (summary used in results.json).
"""
import sys, re
sys.path.insert(0, '/home/claude/hist/elections-since-1832/code')
from common import *

W = json.load(gzip.open(DATA_IN + 'elec1832_wiki_infobox_v1.json.gz'))['pages']
K = pd.read_csv(OUT + 'candidates.csv', dtype={'election': str})
mine = K[K.elected].groupby(['election', 'family']).size().unstack(fill_value=0)


def clean(s):
    s = re.sub(r'<ref.*?(</ref>|/>)', '', s, flags=re.S)
    s = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]*)\]\]', r'\1', s)
    s = re.sub(r"'''?", '', s)
    return s.strip()


def fam(p):
    p = p.lower()
    if 'liberal unionist' in p and 'conservative' not in p: return 'LU'
    if 'national liberal' in p or 'liberal national' in p or 'national labour' in p: return 'ALLY'
    if 'conservative' in p or 'tory' in p or 'unionist party' == p.strip() or p.strip().startswith('unionist'): return 'CON'
    if 'labour' in p and 'liberal' not in p: return 'LAB'
    if 'whig' in p or 'liberal' in p or 'alliance' in p and 'sdp' in p: return 'LIB'
    if 'repeal' in p or 'irish parliamentary' in p or 'home rule' in p or 'irish nationalist' in p or 'irish national' in p: return 'IRN'
    if 'scottish national' in p: return 'SNP'
    return None


rows = []
for e in ELECTIONS:
    t = W[e + ' United Kingdom general election']['lead']
    vals = dict(re.findall(r'\|\s*(party\d+|seats\d+)\s*=\s*([^\n]*)', t))
    for k, v in vals.items():
        if not k.startswith('party'):
            continue
        n = k[5:]
        s = re.search(r'\d[\d,]*', clean(vals.get('seats' + n, '')))
        if not s:
            continue
        f = fam(clean(v))
        rows.append(dict(election=e, party=clean(v), family=f, wiki_seats=int(s.group().replace(',', ''))))
V = pd.DataFrame(rows)
out = []
for e, g in V.groupby('election', sort=False):
    comb = {}
    for r in g.itertuples():
        if r.family:
            comb[r.family] = comb.get(r.family, 0) + r.wiki_seats
    for f in ['CON', 'LIB', 'LAB']:
        if f not in comb:
            continue
        mv = mine.loc[e].get(f, 0)
        if f == 'CON':
            # infoboxes before 1912 often combine Conservatives and Liberal Unionists
            lu_in = any(('liberal unionist' in p.lower() and 'conservative' in p.lower()) for p in g.party)
            if lu_in or 'LU' not in comb:
                mv += mine.loc[e].get('LU', 0)
        out.append(dict(election=e, family=f, wikipedia=comb[f], this_study=int(mv), diff=int(mv - comb[f])))
O = pd.DataFrame(out)
O['eidx'] = O.election.map(ELECTIONS.index); O = O.sort_values(['eidx', 'family']).drop(columns='eidx')
O.to_csv(WORK + 'validate.csv', index=False)
print(O.pivot(index='election', columns='family', values='diff').reindex(ELECTIONS).to_string())
s = dict(compared=len(O), exact=int((O['diff'] == 0).sum()), within2=int((O['diff'].abs() <= 2).sum()), within5=int((O['diff'].abs() <= 5).sum()),
         max_abs=int(O['diff'].abs().max()), median_abs=float(O['diff'].abs().median()), from1918_within2=int((O[O.election.map(ELECTIONS.index) >= 20]['diff'].abs() <= 2).sum()),
         from1918_n=int((O.election.map(ELECTIONS.index) >= 20).sum()))
print(s)
json.dump(s, open(WORK + 'validate.json', 'w'))
print(O[O['diff'].abs() > 5].to_string())
