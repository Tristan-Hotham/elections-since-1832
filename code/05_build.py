"""Assemble the clean tables: one row per contest and per candidate, 1832 to 2024.

Inputs: work/contests_1832_2019.csv and work/candidates_1832_2019.csv (02_contests.py),
work/districts_geo.csv (04_geocode.py), the Commons Library 2024 and notional 2019 files.
Outputs data/contests.csv, data/candidates.csv, work/notional2019.csv.
"""
import sys
sys.path.insert(0, '/home/claude/hist/elections-since-1832/code')
from common import *
from parties import family, FAM_LABEL

C = pd.read_csv(WORK + 'contests_1832_2019.csv.gz')
K = pd.read_csv(WORK + 'candidates_1832_2019.csv.gz')
geo = pd.read_csv(WORK + 'districts_geo.csv').set_index('d')
m, d = load_wikidata()
dl = d.drop_duplicates('d').set_index('d')['dL']

# contests the matcher could not tie to a Wikidata item: all single-member boroughs, placed at the town
UNM = {'Montgomery Boroughs': 'Montgomery', 'Cardigan Boroughs': 'Cardigan', 'Swansea Town': 'Swansea', 'Handsworth': 'Handsworth',
       'Southend-on-Sea': 'Southend-on-Sea', 'Louth': 'Louth'}
osn = pd.read_csv('/home/claude/hist/osnames_gb.tsv', sep='\t', usecols=['name1', 'name2', 'local_type', 'lat', 'lon', 'county'], dtype=str)
osn = osn[osn.local_type.isin(['City', 'Town', 'Suburban Area'])]


def osn_pt(name, west_of=None):
    x = osn[(osn.name1 == name) | (osn.name2 == name)]
    if west_of is not None:
        x = x[x.lon.astype(float) < west_of]
    x = x.sort_values('local_type')
    return float(x.lon.iloc[0]), float(x.lat.iloc[0])


UNM_PT = {k: osn_pt(v, -1.9 if v == 'Handsworth' else None) for k, v in UNM.items()}  # the Birmingham Handsworth

lon, lat, how, nat = [], [], [], []
for r in C.itertuples():
    if isinstance(r.wikidata, str) and r.wikidata in geo.index:
        g = geo.loc[r.wikidata]
        lon.append(g.lon); lat.append(g.lat); how.append(g.how); nat.append(g.nation)
    else:
        a, b = UNM_PT[r.constituency]
        lon.append(a); lat.append(b); how.append('OS Open Names "%s" (no Wikidata match)' % UNM[r.constituency])
        nat.append('Wales' if r.constituency in ('Montgomery Boroughs', 'Cardigan Boroughs', 'Swansea Town') else 'England')
C['lon'], C['lat'], C['place_source'], C['nation'] = lon, lat, how, nat
pre = C.election.map(lambda e: ELECTIONS.index(e) < ELECTIONS.index('1922'))
C.loc[pre & C.nation.isin(['Ireland', 'Northern Ireland']), 'nation'] = 'Ireland'

# ---- 2024 from the Commons Library
H = load_hoc(); cols = H['columns']


def hoc(key):
    x = pd.DataFrame(H['data'][key], columns=cols)
    x = x[x['Candidate is notional political party aggregate'] != 'true']
    return x


x = hoc('2024')
w24 = m[m.gek == '2024'].assign(dL=lambda t: t.d.map(dl))
name2d = dict(zip(w24.dL, w24.d))
name2d['Caerfyrddin'] = next((q for q, l in name2d.items() if False), None) or w24[~w24.dL.isin(set(x['Constituency name']))].d.iloc[0]
rows_c, rows_k = [], []
for con, cs in x.groupby('Constituency name'):
    q = name2d.get(con)
    g = geo.loc[q]
    elect = int(cs['Electorate'].iloc[0]); valid = int(cs['Election valid vote count'].iloc[0])
    rows_c.append(dict(election='2024', date='2024-07-04', constituency=con, wikidata=q, match='name', seats=1, uncontested=False,
                       candidates=len(cs), turnout=round(100 * valid / elect, 1), votes_cast=valid, lon=g.lon, lat=g.lat,
                       place_source=g.how, nation=cs['Country name'].iloc[0]))
    for _, r in cs.iterrows():
        party = r['Main party name'] or ('Speaker' if r['Candidate is standing as Commons Speaker'] == 'true' else 'Independent')
        rows_k.append(dict(election='2024', constituency=con, candidate='%s, %s' % (r['Candidate family name'], r['Candidate given name']),
                           party=party, votes=int(r['Candidate vote count']), elected=r['Candidate result position'] == '1'))
C = pd.concat([C, pd.DataFrame(rows_c)], ignore_index=True)
K = pd.concat([K, pd.DataFrame(rows_k)], ignore_index=True)

# nation for 2010 to 2019 from the Commons Library file where names agree (checks the point-in-polygon nation)
chk = 0; bad = []
for key in ['2010', '2015', '2017', '2019']:
    y = hoc(key).drop_duplicates('Constituency name').set_index('Constituency name')['Country name']
    for r in C[C.election == key].itertuples():
        if r.constituency in y.index:
            chk += 1
            if y[r.constituency] != r.nation:
                bad.append((key, r.constituency, r.nation, y[r.constituency]))
print('nation check 2010 to 2019:', chk, 'compared,', len(bad), 'differ', bad[:5])
json.dump({'compared': chk, 'differ': len(bad)}, open(WORK + 'nation_check.json', 'w'))

# families
irish = dict(zip(zip(C.election, C.constituency), C.nation.isin(['Ireland', 'Northern Ireland'])))
K['family'] = [family(p, e, irish.get((e, c), False)) for p, e, c in zip(K.party, K.election, K.constituency)]
tot = K.groupby(['election', 'constituency']).votes.transform('sum')
K['share'] = (100 * K.votes / tot).round(2)
unc = dict(zip(zip(C.election, C.constituency), C.uncontested))
K.loc[[unc[(e, c)] for e, c in zip(K.election, K.constituency)], 'share'] = None
C['date'] = C['date'].astype(str)
order = {e: i for i, e in enumerate(ELECTIONS)}
C['eidx'] = C.election.map(order); K['eidx'] = K.election.map(order)
C = C.sort_values(['eidx', 'constituency']).drop(columns='eidx')
K = K.sort_values(['eidx', 'constituency', 'votes'], ascending=[True, True, False]).drop(columns='eidx')
C['lon'] = C.lon.round(4); C['lat'] = C.lat.round(4)
geo_out = geo.reset_index()[['d', 'label', 'lon', 'lat', 'nation', 'how']].rename(columns={'d': 'wikidata', 'how': 'place_source'})
geo_out['lon'] = geo_out.lon.round(4); geo_out['lat'] = geo_out.lat.round(4)
geo_out.to_csv(OUT + 'constituency_places.csv', index=False)
C.loc[C.wikidata.isna() | (C.wikidata == ''), 'wikidata'] = ''
C = C.drop(columns=['place_source', 'match'])
C.to_csv(OUT + 'contests.csv', index=False)
K.to_csv(OUT + 'candidates.csv', index=False)

# notional 2019 on the 2024 boundaries (winner per seat), for the 2019 to 2024 comparison
n = hoc('2019_notional_2024_boundaries')
n = n[n['Candidate result position'] == '1'][['Constituency name', 'Country name', 'English region name', 'Main party name']]
n.columns = ['constituency', 'nation', 'region', 'party_2019_notional']
n.to_csv(WORK + 'notional2019.csv', index=False)
reg24 = hoc('2024').drop_duplicates('Constituency name')[['Constituency name', 'English region name']].rename(columns={'Constituency name': 'constituency', 'English region name': 'region'})
reg24.to_csv(WORK + 'regions2024.csv', index=False)
r19 = hoc('2019').drop_duplicates('Constituency name')[['Constituency name', 'English region name', 'Country name']].rename(columns={'Constituency name': 'constituency', 'English region name': 'region', 'Country name': 'nation'})
r19.to_csv(WORK + 'regions2019.csv', index=False)
r17 = hoc('2017').drop_duplicates('Constituency name')[['Constituency name', 'English region name']].rename(columns={'Constituency name': 'constituency', 'English region name': 'region'})
r17.to_csv(WORK + 'regions2017.csv', index=False)
print(C.groupby('election', sort=False).seats.sum().tail(3).to_string())
print(K[K.elected].groupby(['election', 'family']).size().unstack(fill_value=0).loc[['1832', '1906', '1924', '1945', '1997', '2019', '2024']].to_string())
print('OTH winners sample', K[K.elected & (K.family == 'OTH')].party.value_counts().head(20).to_dict())
