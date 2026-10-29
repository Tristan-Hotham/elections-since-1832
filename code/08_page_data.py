"""Compact files for the page.

data/page/dots.json: for every election, one dot per seat (two for a two-member seat), at the
constituency's point, spread apart so that dots do not overlap (each dot is pushed out of its
neighbours' way and pulled back towards its own point; London and the big cities swell).
data/page/e<i>.json: candidates for each election, loaded when needed.
data/page/places.json: towns for the search box and the place names layer.
"""
import sys, math, zipfile, io
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, '/home/claude/hist/elections-since-1832/code')
from common import *
from parties import FAMILIES

P = OUT + 'page/'
os.makedirs(P, exist_ok=True) if False else None
import os
os.makedirs(P, exist_ok=True)
C = pd.read_csv(OUT + 'contests.csv', dtype={'election': str, 'wikidata': str})
K = pd.read_csv(OUT + 'candidates.csv', dtype={'election': str})
fams = [f for f, _, _ in FAMILIES]
fi = {f: i for i, f in enumerate(fams)}
NATS = ['England', 'Scotland', 'Wales', 'Ireland', 'Northern Ireland']
KX = 111.32 * math.cos(math.radians(54))
R_KM = 2.7          # dot radius used for the spreading


def spread(x, y, home, iters=220):
    pts = np.c_[x, y].astype(float)
    hp = np.c_[home].astype(float) if False else pts.copy()
    rng = np.random.default_rng(7)
    pts += rng.normal(0, 0.05, pts.shape)
    d2 = 2 * R_KM
    for it in range(iters):
        t = cKDTree(pts)
        pairs = t.query_pairs(d2, output_type='ndarray')
        if len(pairs) == 0 and it > 10:
            break
        if len(pairs):
            a, b = pairs[:, 0], pairs[:, 1]
            v = pts[a] - pts[b]
            dist = np.hypot(v[:, 0], v[:, 1]) + 1e-6
            push = (d2 - dist) / dist * 0.5
            mv = v * push[:, None]
            np.add.at(pts, a, mv * 0.6)
            np.add.at(pts, b, -mv * 0.6)
        pts += (hp - pts) * 0.012
    return pts


elections = []
moved = []
for ei, e in enumerate(ELECTIONS):
    c = C[C.election == e].reset_index(drop=True)
    k = K[K.election == e]
    kk = {con: g for con, g in k.groupby('constituency')}
    xs, ys, ci, fa = [], [], [], []
    contests = []
    for i, r in c.iterrows():
        g = kk[r.constituency]
        won = g[g.elected].sort_values('votes', ascending=False, na_position='last')
        for j, w in enumerate(won.itertuples()):
            xs.append(r.lon * KX + 0.3 * j); ys.append(r.lat * 111.32)
            ci.append(i); fa.append(fi[w.family])
        sh = g[g.share.notna()].groupby('family').share.sum()
        contests.append([r.constituency, int(r.seats), int(bool(r.uncontested)), None if pd.isna(r.turnout) else float(r.turnout),
                         round(r.lon, 3), round(r.lat, 3), NATS.index(r.nation),
                         [[fi[f], round(float(v), 1)] for f, v in sh.sort_values(ascending=False).items()]])
    pts = spread(np.array(xs), np.array(ys), None)
    dk = np.hypot(pts[:, 0] - np.array(xs), pts[:, 1] - np.array(ys))
    moved.append(float(np.median(dk)))
    lon = (pts[:, 0] / KX).round(3); lat = (pts[:, 1] / 111.32).round(3)
    elections.append({'name': e, 'date': c.date.iloc[0], 'lon': lon.tolist(), 'lat': lat.tolist(), 'c': ci, 'f': fa, 'contests': contests})
    # candidates file
    parties = sorted(k.party.unique())
    det = []
    for r in c.itertuples():
        g = kk[r.constituency].sort_values('votes', ascending=False, na_position='last')
        det.append([[w.candidate, w.party, fi[w.family], None if pd.isna(w.votes) else int(w.votes), int(bool(w.elected))] for w in g.itertuples()])
    json.dump({'e': e, 'c': det}, open(P + 'e%02d.json' % ei, 'w'), separators=(',', ':'), ensure_ascii=False)
D = {'fams': [[f, l, k] for f, l, k in FAMILIES], 'nations': NATS, 'elections': elections}
json.dump(D, open(P + 'dots.json', 'w'), separators=(',', ':'), ensure_ascii=False)
print('median shift km per election', [round(m, 1) for m in moved])

# places for search and labels: OS Open Names cities and towns (GB) and GeoNames towns (Ireland and Northern Ireland)
osn = pd.read_csv('/home/claude/hist/osnames_gb.tsv', sep='\t', usecols=['name1', 'name2', 'local_type', 'lat', 'lon', 'county'], dtype=str)
osn = osn[osn.local_type.isin(['City', 'Town', 'Village'])]
rank = {'City': 3, 'Town': 2, 'Village': 0}
pl = [[r.name1, round(float(r.lon), 3), round(float(r.lat), 3), rank[r.local_type], r.county if isinstance(r.county, str) else ''] for r in osn.itertuples()]
with zipfile.ZipFile('/home/claude/hist/_data13/cities15000.zip') as z:
    for line in io.TextIOWrapper(z.open('cities15000.txt'), encoding='utf-8'):
        f = line.split('\t')
        if f[8] == 'IE' or (f[8] == 'GB' and f[10] == 'NIR'):
            pl.append([f[1], round(float(f[5]), 3), round(float(f[4]), 3), 3 if int(f[14]) > 100000 else 2, 'Ireland' if f[8] == 'IE' else 'Northern Ireland'])
json.dump(pl, open(P + 'places.json', 'w'), separators=(',', ':'), ensure_ascii=False)
print(len(pl))
