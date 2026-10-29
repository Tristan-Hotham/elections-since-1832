"""Every number used on the page, in the paper, the blog and the collage: data/results.json.
Also writes data/seats_by_family.csv, data/votes_by_family.csv and data/nations_by_family.csv."""
import sys
import numpy as np
sys.path.insert(0, '/home/claude/hist/elections-since-1832/code')
from common import *
from parties import FAMILIES, FAM_LABEL

C = pd.read_csv(OUT + 'contests.csv', dtype={'election': str})
K = pd.read_csv(OUT + 'candidates.csv', dtype={'election': str})
E = ELECTIONS
idx = {e: i for i, e in enumerate(E)}
W = K[K.elected].merge(C[['election', 'constituency', 'nation', 'seats', 'uncontested']], on=['election', 'constituency'])
R = {}
fams = [f for f, _, _ in FAMILIES]

# ---- overview
R['n_elections'] = len(E)
R['n_contests'] = len(C)
R['n_candidacies'] = len(K)
R['n_mps_elected'] = int(len(W))
R['n_constituency_names'] = int(C.constituency.nunique())
R['first_date'] = C[C.election == '1832'].date.min()
R['seats'] = {e: int(C[C.election == e].seats.sum()) for e in E}

# ---- seats by family
S = W.groupby(['election', 'family']).size().unstack(fill_value=0).reindex(E).reindex(columns=fams, fill_value=0)
S.to_csv(OUT + 'seats_by_family.csv')
R['seats_by_family'] = {e: {f: int(S.loc[e, f]) for f in fams if S.loc[e, f]} for e in E}

# ---- votes by family (contested seats only; every vote counted, so electors in two-member seats count twice)
V = K[K.share.notna()].groupby(['election', 'family']).votes.sum().unstack(fill_value=0).reindex(E).reindex(columns=fams, fill_value=0)
Vs = (100 * V.div(V.sum(axis=1), axis=0)).round(2)
Vs.to_csv(OUT + 'votes_by_family.csv')
R['vote_share_by_family'] = {e: {f: float(Vs.loc[e, f]) for f in fams if Vs.loc[e, f] >= 0.05} for e in E}
R['votes_counted'] = {e: int(V.loc[e].sum()) for e in E}

# ---- uncontested
U = C.groupby('election').apply(lambda g: pd.Series({'seats': g.seats.sum(), 'unc_seats': g[g.uncontested].seats.sum(), 'unc_contests': int(g.uncontested.sum())})).reindex(E)
U['share'] = (100 * U.unc_seats / U.seats).round(1)
R['uncontested'] = {e: {'seats': int(U.loc[e, 'unc_seats']), 'share': float(U.loc[e, 'share'])} for e in E}
R['unc_max'] = {'election': U.share.idxmax(), 'share': float(U.share.max()), 'seats': int(U.loc[U.share.idxmax(), 'unc_seats'])}
last = [e for e in E if U.loc[e, 'unc_seats'] > 0][-1]
R['unc_last'] = {'election': last, 'seats': int(U.loc[last, 'unc_seats'])}
pre1885 = U.loc[E[:E.index('1885')]]
R['unc_1832_1880_share'] = round(100 * pre1885.unc_seats.sum() / pre1885.seats.sum(), 1)
R['unc_total_seats'] = int(U.unc_seats.sum())

# ---- multi-member seats
mm = C[C.seats > 1]
R['multi_member'] = {e: {'contests': int((mm.election == e).sum()), 'seats': int(mm[mm.election == e].seats.sum())} for e in E if (mm.election == e).any()}
R['multi_member_last'] = mm.election.map(idx).max() and E[mm.election.map(idx).max()]
split = []
for (e, c), g in W[W.seats == 2].groupby(['election', 'constituency']):
    split.append((e, g.family.nunique() > 1))
sp = pd.DataFrame(split, columns=['election', 'split'])
R['two_member_split_share_1832_1880'] = round(100 * sp[sp.election.map(idx) < idx['1885']].split.mean(), 1)
R['two_member_split_n_1832_1880'] = int(sp[sp.election.map(idx) < idx['1885']].split.sum())
R['two_member_contests_1832_1880'] = int((sp.election.map(idx) < idx['1885']).sum())

# ---- nations
N = W.groupby(['election', 'nation', 'family']).size().rename('seats').reset_index()
N.to_csv(OUT + 'nations_by_family.csv', index=False)
R['nations'] = {}
for nat in ['England', 'Scotland', 'Wales', 'Ireland', 'Northern Ireland']:
    x = N[N.nation == nat]
    R['nations'][nat] = {e: {r.family: int(r.seats) for r in g.itertuples()} for e, g in x.groupby('election')}

# ---- turnout (median constituency turnout among contested seats; electorates are not in the 1832 to 2019 file)
T = C[~C.uncontested & C.turnout.notna()].groupby('election').turnout.median().reindex(E)
R['turnout_median'] = {e: float(round(T[e], 1)) for e in E}
R['turnout_peak'] = {'election': T.idxmax(), 'value': float(round(T.max(), 1))}
post = T.loc[E[idx['1918']:]]
R['turnout_low_since1918'] = {'election': post.idxmin(), 'value': float(round(post.min(), 1))}
c24 = C[C.election == '2024']
R['turnout_2024_overall'] = round(100 * c24.votes_cast.sum() / (c24.votes_cast / (c24.turnout / 100)).sum(), 1)

# ---- stories
def fam_seats(e, f): return int(S.loc[e, f])
R['lib'] = {e: fam_seats(e, 'LIB') for e in E}
R['lab'] = {e: fam_seats(e, 'LAB') for e in E}
R['con'] = {e: fam_seats(e, 'CON') for e in E}
R['lib_min'] = {'election': S.LIB.loc[E[idx['1918']:]].idxmin(), 'seats': int(S.LIB.loc[E[idx['1918']:]].min())}
R['lab_first'] = next(e for e in E if S.loc[e, 'LAB'] > 0)
R['lab_overtakes_lib'] = next(e for e in E if S.loc[e, 'LAB'] > S.loc[e, 'LIB'])
R['lib_vote'] = {e: round(float(Vs.loc[e, 'LIB']), 1) for e in E}
R['lab_vote'] = {e: round(float(Vs.loc[e, 'LAB']), 1) for e in E}
R['con_vote'] = {e: round(float(Vs.loc[e, 'CON']), 1) for e in E}

def nat_share(nat, e, fs):
    x = N[(N.nation == nat) & (N.election == e)]
    t = x.seats.sum()
    return int(x[x.family.isin(fs)].seats.sum()), int(t)
R['scot'] = {e: dict(zip(['snp', 'lab', 'con', 'lib'], [nat_share('Scotland', e, [f])[0] for f in ['SNP', 'LAB', 'CON', 'LIB']]), total=nat_share('Scotland', e, ['CON'])[1]) for e in E}
R['wales'] = {e: dict(zip(['lab', 'con', 'lib', 'pc'], [nat_share('Wales', e, [f])[0] for f in ['LAB', 'CON', 'LIB', 'PC']]), total=nat_share('Wales', e, ['CON'])[1]) for e in E}
R['wales_no_con'] = [e for e in E if R['wales'][e]['con'] == 0 and R['wales'][e]['total'] > 0]
R['ireland_1918'] = {'sf': nat_share('Ireland', '1918', ['SF'])[0], 'irn': nat_share('Ireland', '1918', ['IRN'])[0], 'con': nat_share('Ireland', '1918', ['CON'])[0], 'total': nat_share('Ireland', '1918', ['SF'])[1]}
R['ireland_1910d'] = {'irn': nat_share('Ireland', 'December 1910', ['IRN'])[0], 'total': nat_share('Ireland', 'December 1910', ['IRN'])[1]}
# Scottish Conservative and Unionist vote share in 1955 (contested Scottish seats)
ks = K[K.share.notna()].merge(C[['election', 'constituency', 'nation']], on=['election', 'constituency'])
def nat_vote(nat, e, f):
    x = ks[(ks.nation == nat) & (ks.election == e)]
    return round(100 * x[x.family == f].votes.sum() / x.votes.sum(), 1)
R['scot_con_vote_1955'] = nat_vote('Scotland', '1955', 'CON')
R['scot_snp_vote_2015'] = nat_vote('Scotland', '2015', 'SNP')
R['wales_lab_vote_1966'] = nat_vote('Wales', '1966', 'LAB')
R['wales_lib_vote_1906'] = nat_vote('Wales', '1906', 'LIB')

# Red Wall: seats in the North East, North West, Yorkshire and the Humber, East Midlands, West Midlands and Wales
# that Labour won in 2017 and the Conservatives won in 2019 (unchanged boundaries)
RW_REG = ['North East', 'North West', 'Yorkshire and The Humber', 'East Midlands', 'West Midlands']
reg19 = pd.read_csv(WORK + 'regions2019.csv')
w17 = W[W.election == '2017'].set_index('constituency').family
w19 = W[W.election == '2019'].set_index('constituency').family
reg19['in_area'] = reg19.region.isin(RW_REG) | (reg19.nation == 'Wales')
area = set(reg19[reg19.in_area].constituency)
rw = sorted(c for c in w19.index if c in area and w19[c] == 'CON' and w17.get(c) == 'LAB')
R['redwall'] = {'regions': RW_REG + ['Wales'], 'seats_2019': len(rw), 'area_seats': len(area), 'lab_2017_in_area': int(sum(1 for c in area if w17.get(c) == 'LAB')),
                'lab_2019_in_area': int(sum(1 for c in area if w19.get(c) == 'LAB'))}
open(WORK + 'redwall_2019.txt', 'w').write('\n'.join(rw))
# how long Labour had held them: consecutive Labour wins before 2019 by constituency name (names can hide boundary changes)
streak = []
for c in rw:
    n = 0
    for e in reversed(E[:idx['2019']]):
        x = W[(W.election == e) & (W.constituency == c)]
        if len(x) and (x.family == 'LAB').all():
            n += 1
        else:
            break
    streak.append(n)
R['redwall']['median_prior_lab_wins'] = float(np.median(streak)) if streak else None
R['redwall']['held_since_1945_or_earlier'] = int(sum(1 for c, s in zip(rw, streak) if s >= idx['2017'] - idx['1945'] + 1))
# 2024: notional 2019 results on the new boundaries
n19 = pd.read_csv(WORK + 'notional2019.csv')
n19['in_area'] = n19.region.isin(RW_REG) | (n19.nation == 'Wales')
w24 = W[W.election == '2024'].set_index('constituency').family
a = n19[n19.in_area & (n19.party_2019_notional == 'Conservative')]
R['redwall']['notional_con_2019_area_2024seats'] = len(a)
R['redwall']['of_which_2024'] = {f: int(v) for f, v in a.constituency.map(w24).value_counts().items()}
allc = n19[n19.party_2019_notional == 'Conservative']
R['con_notional_2019_seats'] = len(allc)
R['con_notional_2019_kept_2024'] = int((allc.constituency.map(w24) == 'CON').sum())
R['flows_2019n_2024'] = {f'{p}->{f}': int(v) for (p, f), v in pd.crosstab(n19.party_2019_notional, n19.constituency.map(w24)).stack().items() if v}

# 2024 headline and the gap between seats and votes
for e in ['2024', '2019', '1997', '1983', '1945', '1906']:
    R['seat_share_' + e] = {f: round(100 * S.loc[e, f] / S.loc[e].sum(), 1) for f in fams if S.loc[e, f]}
R['lab_2024_vote'] = round(float(Vs.loc['2024', 'LAB']), 1); R['ref_2024_vote'] = round(float(Vs.loc['2024', 'REF']), 1); R['ref_2024_seats'] = fam_seats('2024', 'REF')
R['lib_1983_vote'] = round(float(Vs.loc['1983', 'LIB']), 1); R['lib_1983_seats'] = fam_seats('1983', 'LIB')

# largest majority government by family seat share
R['top_seat_shares'] = sorted(([e, f, round(100 * S.loc[e, f] / S.loc[e].sum(), 1)] for e in E for f in ['CON', 'LIB', 'LAB']), key=lambda t: -t[2])[:5]
R['validate'] = json.load(open(WORK + 'validate.json'))
R['nation_check'] = json.load(open(WORK + 'nation_check.json'))
R['n_party_labels_1832_2019'] = int(load_parliament().party.nunique())
R['geocode_test'] = json.load(open(WORK + 'geocode_test.json'))
geo = pd.read_csv(WORK + 'districts_geo.csv')
R['places'] = {'districts': len(geo), 'own_coords': int(geo.how.str.startswith('wikidata P625').sum()), 'stand_in': int(geo.how.str.startswith('stand-in').sum()),
               'university': int(geo.how.str.startswith('hand').sum())}
R['places']['looked_up'] = R['places']['districts'] - R['places']['own_coords'] - R['places']['stand_in'] - R['places']['university']
mt = pd.read_csv(WORK + 'match.csv')
R['match'] = {'contests': len(mt), 'exact': int((mt.how == 'exact').sum()), 'fuzzy': int(mt.how.str.startswith('fuzzy').sum()), 'unmatched': int((mt.how == 'unmatched').sum())}
json.dump(R, open(OUT + 'results.json', 'w'), indent=1, default=lambda o: int(o) if isinstance(o, (np.integer,)) else float(o))
for k in ['n_contests', 'n_candidacies', 'n_mps_elected', 'n_constituency_names', 'unc_max', 'unc_last', 'unc_1832_1880_share', 'multi_member_last', 'two_member_split_share_1832_1880',
          'lib_min', 'lab_first', 'lab_overtakes_lib', 'ireland_1918', 'ireland_1910d', 'wales_no_con', 'scot_con_vote_1955', 'scot_snp_vote_2015', 'redwall', 'con_notional_2019_seats', 'con_notional_2019_kept_2024',
          'turnout_peak', 'turnout_low_since1918', 'turnout_2024_overall', 'top_seat_shares', 'places', 'match', 'lib_1983_vote', 'lib_1983_seats', 'ref_2024_vote', 'wales_lab_vote_1966', 'wales_lib_vote_1906']:
    print(k, R[k])
print('scot', {e: R['scot'][e] for e in ['1906', '1955', '1997', '2010', '2015', '2019', '2024']})
print('wales', {e: R['wales'][e] for e in ['1906', '1922', '1966', '1997', '2019', '2024']})
print('lib', {e: R['lib'][e] for e in ['1906', 'December 1910', '1918', '1922', '1924', '1929', '1935', '1945', '1951', '1955', '1997', '2005', '2015', '2024']})
print('vote', {e: (R['lib_vote'][e], R['lab_vote'][e], R['con_vote'][e]) for e in ['1906', '1924', '1945', '1951', '1983', '2024']})
