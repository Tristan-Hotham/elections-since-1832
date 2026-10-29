"""Build one row per contest and one row per candidate, with seats and winners.

Seats per constituency and election = number of members Wikidata records as elected for that
district at that general election (P39 with P2715 and P768), smoothed where a petition or
double return adds an extra name. Winners = all candidates in an uncontested return; otherwise
the top N by votes, N = seats. Where an uncontested return lists more candidates than seats,
Wikidata's member surnames choose. 2024 comes from the Commons Library results file.
"""
import sys, re, collections
sys.path.insert(0, '/home/claude/hist/elections-since-1832/code')
from common import *

m, d = load_wikidata()
m = m[m.gek.isin(ELECTIONS)]
dl = d.drop_duplicates('d').set_index('d')['dL']
mt = pd.read_csv(WORK + 'match.csv')
df = load_parliament()

# ---- seats per district per election
cnt = m.dropna(subset=['d']).groupby(['gek', 'd']).person.nunique()
order = {g: i for i, g in enumerate(ELECTIONS)}
seats = {}
for dq, s in cnt.groupby(level=1):
    s = s.droplevel(1)
    gs = sorted(s.index, key=order.get)
    for i, g in enumerate(gs):
        v = s[g]
        nb = [s[gs[j]] for j in (i - 1, i + 1) if 0 <= j < len(gs) and abs(order[gs[j]] - order[g]) == 1]
        if nb and v > max(nb):
            v = max(nb)   # an extra name from a petition or a double return
        seats[(g, dq)] = int(v)
mt['seats'] = [seats.get((g, q), 1) if isinstance(q, str) else 1 for g, q in zip(mt.gek, mt.d)]


def wsurn(label):
    if not isinstance(label, str):
        return ''
    w = norm(re.sub(r',.*$', '', re.sub(r'\(.*?\)', '', label))).split()
    return w[-1] if w else ''


wsur = m.dropna(subset=['d']).groupby(['gek', 'd']).personL.apply(lambda s: [wsurn(x) for x in s]).to_dict()

rows_c, rows_k = [], []
key = mt.set_index(['gek', 'con'])
for (g, con), cs in df.groupby(['gek', 'con'], sort=False):
    k = key.loc[(g, con)]
    n_seats = int(k.seats)
    cs = cs.copy()
    unc = bool(cs.unc.max())
    if unc:
        if len(cs) <= n_seats:
            cs['elected'] = True
        else:  # pick by Wikidata surnames
            ws = wsur.get((g, k.d), [])
            cs['elected'] = [norm(c.split(',')[0]).split()[-1] in ws for c in cs.cand]
            if cs.elected.sum() != n_seats:
                cs['elected'] = [True] * n_seats + [False] * (len(cs) - n_seats)
    else:
        cs = cs.sort_values('votes', ascending=False)
        cs['elected'] = [i < n_seats for i in range(len(cs))]
        # ties at the boundary are rare; flag them
    tv = cs.votes.sum() if not unc else None
    rows_c.append(dict(election=g, date=cs.start.iloc[0], constituency=con, wikidata=k.d if isinstance(k.d, str) else '',
                       match=k.how.split(':')[0], seats=n_seats, uncontested=unc, candidates=len(cs),
                       turnout=cs.turnout.iloc[0] if not unc else None, votes_cast=tv))
    for _, r in cs.iterrows():
        rows_k.append(dict(election=g, constituency=con, candidate=r.cand, party=r.party, votes=r.votes, elected=r.elected))

C = pd.DataFrame(rows_c)
K = pd.DataFrame(rows_k)
C.to_csv(WORK + 'contests_1832_2019.csv.gz', index=False)
K.to_csv(WORK + 'candidates_1832_2019.csv.gz', index=False)
print(C.groupby('election', sort=False).seats.sum().to_string())
w = K[K.elected]
print(w.groupby('party').size().sort_values(ascending=False).to_string())

# validation: elected surnames vs Wikidata members
agree = tot = 0
for (g, con), cs in w.groupby(['election', 'constituency']):
    q = key.loc[(g, con)].d
    if not isinstance(q, str):
        continue
    ws = wsur.get((g, q), [])
    for c in cs.candidate:
        tot += 1
        s = norm(c.split(',')[0]).split()
        agree += bool(s) and (s[-1] in ws or any(x in ' '.join(ws) for x in s))
print('winner surname agreement', agree, tot, agree / tot)
