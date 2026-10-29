"""Place every constituency (Wikidata district item) at a point.

Order of preference:
 1. the district's own Wikidata coordinates (P625);
 2. coordinates of another constituency item with the same name as the place part of this one;
 3. the place part looked up in Wikidata (counties first for county seats, then cities, towns,
    boroughs and districts) or, in Great Britain, OS Open Names (cities, towns, suburbs, villages);
 4. a short hand list for university seats and a few others (below), with the reason.
Divisions named North, South, East or West are nudged that way from the place point (about
15 km for counties, 2.5 km for towns), so that they sit on the right side of each other; the
page then spreads overlapping dots apart. These are display points, not boundaries.
Writes work/districts_geo.csv.
"""
import sys, math, collections, re
sys.path.insert(0, '/home/claude/hist/elections-since-1832/code')
from common import *
from geo_names import candidates, direction
from shapely.geometry import shape, Point

m, d = load_wikidata()
mt = pd.read_csv(WORK + 'match.csv')
G = json.load(gzip.open(DATA_IN + 'elec1832_gazetteer_v1.json.gz'))
gz = pd.DataFrame(G['rows'], columns=G['columns'])

NAT = {f['properties']['nation']: shape(f['geometry']) for f in json.load(open(OUT + 'nations.geojson'))['features']}


def nation_of(lon, lat):
    p = Point(lon, lat)
    for k, s in NAT.items():
        if s.contains(p):
            return k
    best = min(NAT, key=lambda k: NAT[k].distance(p))
    return best


T1 = {'Q67376938', 'Q1138494', 'Q180673', 'Q769603', 'Q1350181', 'Q179872', 'Q202435', 'Q7309443'}
T2 = {'Q515', 'Q1549591', 'Q3957', 'Q18511725', 'Q1357964', 'Q21503295', 'Q1006876', 'Q7543008', 'Q518343', 'Q1002812',
      'Q2755753', 'Q188509', 'Q7897276', 'Q486972', 'Q1187580', 'Q1136601', 'Q2630741', 'Q123705', 'Q3257686'}
T3 = {'Q27971968', 'Q27990982', 'Q44710774', 'Q1115575', 'Q532', 'Q5084', 'Q2151232', 'Q5124673', 'Q3910694', 'Q102496',
      'Q2500304', 'Q589282', 'Q853565', 'Q19953632'}
SUB0 = {'Q515', 'Q1549591', 'Q3957', 'Q18511725', 'Q1357964', 'Q21503295', 'Q1006876', 'Q7543008', 'Q518343', 'Q1002812', 'Q1187580', 'Q1136601'}
SUB1 = {'Q2755753', 'Q188509', 'Q7897276', 'Q2630741'}
gz['tier'] = gz['class'].map(lambda c: 1 if c in T1 else (2 if c in SUB0 else 2.3 if c in SUB1 else 2.6) if c in T2 else 3 if c in T3 else 9)
gz = gz[gz.tier < 9]
gzb = gz.sort_values('tier').groupby(['label', 'item']).agg(lon=('lon', 'first'), lat=('lat', 'first'), tier=('tier', 'min'), ncls=('class', 'nunique')).reset_index()
gzb['nation'] = [nation_of(a, b) for a, b in zip(gzb.lon, gzb.lat)]

osn = pd.read_csv('/home/claude/hist/osnames_gb.tsv', sep='\t', usecols=['name1', 'name2', 'local_type', 'lat', 'lon', 'county', 'country'], dtype=str)
osn = osn[osn.local_type.isin(['City', 'Town', 'Suburban Area', 'Village', 'Other Settlement', 'Hamlet'])]
osn['rank'] = osn.local_type.map({'City': 0, 'Town': 1, 'Suburban Area': 2, 'Village': 3, 'Other Settlement': 4, 'Hamlet': 5})
osn['lat'] = osn.lat.astype(float); osn['lon'] = osn.lon.astype(float)
osn_by = collections.defaultdict(list)
for r in osn.itertuples():
    for n in (r.name1, r.name2):
        if isinstance(n, str):
            osn_by[n].append((r.rank, r.lon, r.lat, r.country, r.county))

# district metadata and hints
dd = d.groupby('d').agg(dL=('dL', 'first'), desc=('dDesc', 'first'), coord=('coord', lambda s: next((x for x in s if isinstance(x, str) and x.startswith('POINT')), None)),
                        admin=('adminL', lambda s: '|'.join(sorted({x for x in s if isinstance(x, str)}))), country=('country', lambda s: '|'.join(sorted({x for x in s if isinstance(x, str)}))))
used = set(mt.d.dropna()) | set(m[m.gek == '2024'].d.dropna())
dd = dd[dd.index.isin(used)]
ENG = {'South East England', 'North West England', 'West Midlands', 'South West England', 'East of England', 'Yorkshire and the Humber',
       'East Midlands', 'North East England', 'Greater London', 'London', 'England'}


def hint(row):
    a = row.admin or ''
    if 'Northern Ireland' in a: return {'Northern Ireland'}
    if 'Ireland' in a or 'wd:Q27' == row.country: return {'Ireland', 'Northern Ireland'}
    if 'Scotland' in a: return {'Scotland'}
    if 'Wales' in a: return {'Wales'}
    if any(x in a for x in ENG): return {'England'}
    return None


def pt(s):
    mm = re.match(r'POINT\(([-\d.]+) ([-\d.]+)\)', s)
    return float(mm.group(1)), float(mm.group(2))


with_coord = {}
for q, r in dd.iterrows():
    if isinstance(r.coord, str):
        with_coord.setdefault(r.dL, pt(r.coord))

COUNTYISH = re.compile(r'(shire|^County |^Antrim|^Armagh|^Carlow|^Cavan|^Clare|^Cork|^Donegal|^Down|^Dublin County|^Fermanagh|^Galway|^Kerry|^Kildare|^Kilkenny|^Leitrim|^Limerick|^Londonderry|^Longford|^Louth|^Mayo|^Meath|^Monaghan|^Queen|^King|^Roscommon|^Sligo|^Tipperary|^Tyrone|^Waterford|^Westmeath|^Wexford|^Wicklow|^Cornwall|^Devon|^Dorset|^Kent|^Essex|^Middlesex|^Norfolk|^Suffolk|^Surrey|^Sussex|^Cumberland|^Durham|^Northumberland|^Westmorland|^Rutland|^Fife|^Angus|^Argyll|^Caithness|^Sutherland|^Orkney|^Shetland|^Moray|^Galloway|^Lothian|^Anglesey|^Merioneth|^Montgomery|^Radnor|^Brecon|^Cardigan|^Carmarthen|^Pembroke|^Glamorgan|^Monmouth|^Denbigh|^Flint)')

# hand placements: the university seats have no area; they are placed at the university town.
HAND = {
    'Oxford University': ('Oxford', -1.2546, 51.7548), 'Cambridge University': ('Cambridge', 0.1167, 52.2053),
    'Dublin University': ('Trinity College Dublin', -6.2546, 53.3438), 'London University': ('Bloomsbury, London', -0.1290, 51.5220),
    'University of London': ('Bloomsbury, London', -0.1290, 51.5220),
    'Glasgow and Aberdeen Universities': ('Glasgow', -4.2886, 55.8721), 'Edinburgh and St Andrews Universities': ('Edinburgh', -3.1883, 55.9474),
    'Combined Scottish Universities': ('Edinburgh', -3.1883, 55.9474), 'Combined English Universities': ('Manchester', -2.2340, 53.4668),
    'University of Wales': ('Aberystwyth', -4.0640, 52.4153), "Queen's University of Belfast": ('Belfast', -5.9350, 54.5844),
    'National University of Ireland': ('Dublin', -6.2603, 53.3498),
}

# Stand-in towns for the constituencies the steps above could not place (my choice of a town
# inside or central to the seat; coordinates from OS Open Names, or GeoNames for Ireland).
STAND = {'Linlithgowshire': 'Linlithgow', 'Isle of Thanet': 'Margate', 'North Tayside': 'Blairgowrie', 'Somersetshire Northern': 'Keynsham',
         "King's County": 'Tullamore', "Queen's County": 'Portlaoise', 'Leix': 'Portlaoise', 'Ossory': 'Portlaoise', 'Argyllshire': 'Inveraray',
         'Bucklow': 'Knutsford', 'Buckrose': 'Driffield', 'Carshalton': 'Carshalton', 'Clwyd North West': 'Abergele', 'Clwyd South West': 'Llangollen',
         'Clydesdale': 'Lanark', 'Cunninghame North': 'Largs', 'Cunninghame South': 'Irvine', 'East Riding of Yorkshire': 'Beverley',
         'Eastern West Riding of Yorkshire': 'Tadcaster', 'Eifion': 'Pwllheli', 'Forfarshire': 'Forfar', 'Galloway': 'Newton Stewart',
         'Galloway and Upper Nithsdale': 'Castle Douglas', 'Haddingtonshire': 'Haddington', 'Hallamshire': 'Ecclesfield', 'Howdenshire': 'Howden',
         'East Grinstead': 'East Grinstead', 'Isle of Ely': 'Ely', 'Lonsdale': 'Carnforth', 'North Lonsdale': 'Ulverston',
         'Kingston-upon-Thames': 'Kingston upon Thames', 'Monklands East': 'Airdrie', 'Monklands West': 'Coatbridge',
         'North Riding of Yorkshire': 'Northallerton', 'Northern West Riding of Yorkshire': 'Skipton', 'Southern West Riding of Yorkshire': 'Rotherham',
         'Ochil': 'Alloa', 'Osgoldcross': 'Snaith', 'Radcliffe-cum-Farnworth': 'Radcliffe', 'Ravensbourne': 'West Wickham', 'South Hams': 'Totnes',
         'South Molton': 'South Molton', 'St Marylebone': 'Marylebone', 'Torrington': 'Great Torrington', 'Tunbridge': 'Tonbridge',
         'Tyneside': 'Wallsend', 'West Bromwich': 'West Bromwich', 'West Lothian': 'Bathgate', 'West Riding of Yorkshire': 'Wakefield'}
import zipfile, io
GN = {}
with zipfile.ZipFile('/home/claude/hist/_data13/cities15000.zip') as z:
    for line in io.TextIOWrapper(z.open('cities15000.txt'), encoding='utf-8'):
        f = line.split('\t')
        if f[8] == 'IE':
            GN[f[1]] = (float(f[5]), float(f[4]))

# place parts that are ambiguous or abbreviated in constituency names
ALIAS = {'Stockton': 'Stockton-on-Tees', 'Houghton': 'Houghton-le-Spring', 'Holland': 'Spalding', 'Burton': 'Burton upon Trent',
         'Henley': 'Henley-on-Thames', 'Gordon': 'Inverurie', 'Gillingham': 'Chatham', 'Barons Court': 'Fulham', 'Richmond Park': 'Richmond', 'Newton': 'Newton-le-Willows'}
CTY = {f['properties']['county']: shape(f['geometry']).buffer(0) for f in json.load(open('/home/claude/hist/bread-rolls/data/counties.geojson'))['features']}
LAND = None


def on_land(lon, lat):
    p = Point(lon, lat)
    return any(sh.distance(p) < 0.05 for sh in NAT.values()) and not (-4.85 < lon < -4.3 and 54.04 < lat < 54.42)


def ok_point(lon, lat, r):
    if not on_land(lon, lat):
        return False
    areas = [a for a in str(r.admin).split('|') if a in CTY] if r.dL not in LABEL_ALIAS else []
    br = re.findall(r'\((.*?)\)', r.dL)
    areas += [b for b in br if b in CTY]
    if areas and min(CTY[a].distance(Point(lon, lat)) for a in areas) > 0.12:
        return False
    return True


# whole-label stand-ins where the name's parts mislead the lookup (London divisions, valleys)
LABEL_ALIAS = {'St George': 'Wapping', 'Tower Hamlets Stepney': 'Stepney', 'Newington West': 'Walworth', 'Newington Walworth': 'Walworth',
               'Dearne Valley': 'Wath upon Dearne', 'Sheffield Park': 'Sheffield', 'East Lindsey': 'Horncastle', 'Rowley Regis and Tipton': 'Rowley Regis'}
IN_LONDON = {'Wapping', 'Walworth', 'Stepney'}
ALIAS.update({'Waterloo': 'Crosby', 'Ross': 'Ross-on-Wye', 'Norwood': 'West Norwood', 'Ince': 'Ince-in-Makerfield', 'Southend': 'Southend-on-Sea'})
TEST = len(sys.argv) > 1 and sys.argv[1] == 'test'
rows = []
for q, r in dd.iterrows():
    L = r.dL
    h = hint(r)
    how = src = None
    lonlat = None
    if L in HAND or any(L.startswith(k) for k in HAND):
        k = L if L in HAND else next(k for k in HAND if L.startswith(k))
        nm, lo, la = HAND[k]; lonlat = (lo, la); how = 'hand: university seat placed at ' + nm
    elif isinstance(r.coord, str) and not TEST:
        lonlat = pt(r.coord); how = 'wikidata P625'
    else:
        if L in LABEL_ALIAS or any(L.startswith(k + ' ') for k in ('East Ham', 'West Ham')):
            cands0 = [LABEL_ALIAS.get(L) or ('East Ham' if L.startswith('East Ham') else 'West Ham')]
        else:
            cands0 = None
        cands = candidates(L)
        raw = [p.strip() for p in re.split(r',| and ', L) if p.strip()]
        cands = [L] + [p for p in raw if p not in cands and p != L] + [c for c in cands if c != L]
        cands = [ALIAS.get(c, c) for c in cands]
        if cands0:
            cands = cands0
        # "Liverpool Scotland", "Glasgow Govan": a sub-place must lie near its main town
        subs, parent = set(), None
        core = re.sub(r'\(.*?\)', '', L).strip().split()
        if len(core) >= 2 and not cands0:
            main = core[0]
            if main not in ('North', 'South', 'East', 'West', 'Central', 'Mid', 'St', 'Great', 'Isle', 'City', 'New', 'Old'):
                o = sorted(x for x in osn_by.get(main, []) if x[0] <= 1)
                gm = gzb[(gzb.label == main) & (gzb.tier < 2.5)].sort_values(['tier', 'ncls'], ascending=[True, False])
                gm = gm[[ok_point(a, b, r) for a, b in zip(gm.lon, gm.lat)]]
                if len(gm):
                    parent = (gm.lon.iloc[0], gm.lat.iloc[0])
                elif o:
                    parent = (o[0][1], o[0][2])
                subs = {c for c in cands if c != main and main not in c}
        for c in cands:
            if c in with_coord and not TEST:
                lonlat = with_coord[c]; how = 'wikidata P625 of constituency "%s"' % c; break
            countyish = bool(COUNTYISH.search(c))
            g = gzb[gzb.label.isin([c, 'County ' + c] if countyish else [c])]
            if h:
                g = g[g.nation.isin(h)]
            g = g[[ok_point(a, b, r) for a, b in zip(g.lon, g.lat)]] if len(g) else g
            if parent is not None and c in subs and len(g):
                g = g[[math.hypot((a - parent[0]) * 0.6, b - parent[1]) < 0.07 for a, b in zip(g.lon, g.lat)]]
            if countyish:
                g1 = g[g.tier == 1]
                if len(g1):
                    lonlat = (g1.lon.mean(), g1.lat.mean()); how = 'wikidata county "%s"' % c; break
            g2 = g[(g.tier >= 2) & (g.tier < 2.5)].sort_values(['tier', 'ncls'], ascending=[True, False])
            if len(g2):
                lonlat = (g2.lon.iloc[0], g2.lat.iloc[0]); how = 'wikidata place "%s" (%s)' % (c, g2.item.iloc[0]); break
            if not (h and h <= {'Ireland', 'Northern Ireland'}):
                o = sorted(osn_by.get(c, []))
                if h:
                    o = [x for x in o if x[3] in h]
                o = [x for x in o if ok_point(x[1], x[2], r)]
                if c in IN_LONDON:
                    o = [x for x in o if x[4] == 'Greater London']
                if parent is not None and c in subs:
                    o = [x for x in o if math.hypot((x[1] - parent[0]) * 0.6, x[2] - parent[1]) < 0.07]
                if o:
                    lonlat = (o[0][1], o[0][2]); how = 'OS Open Names "%s"' % c; break
            g3 = g[g.tier <= 3].sort_values(['tier', 'ncls'], ascending=[True, False])
            if len(g3):
                lonlat = (g3.lon.iloc[0], g3.lat.iloc[0]); how = 'wikidata item "%s" (%s)' % (c, g3.item.iloc[0]); break
    if lonlat is None and r.dL in STAND:
        nm = STAND[r.dL]
        if nm in GN:
            lonlat = GN[nm]; how = 'stand-in town %s (GeoNames)' % nm
        else:
            o = sorted(osn_by.get(nm, []))
            if o:
                lonlat = (o[0][1], o[0][2]); how = 'stand-in town %s (OS Open Names)' % nm
    lo = la = None
    if lonlat:
        lo, la = lonlat
        if not how.startswith('wikidata P625') and not how.startswith('hand') and not how.startswith('stand-in') and '"%s"' % L not in how:
            dx, dy = direction(L)
            k = 15 if (COUNTYISH.search(L) or 'county' in how) else 2.5
            la += dy * k / 111.0
            lo += dx * k / (111.0 * math.cos(math.radians(la)))
            n0 = nation_of(*lonlat)
            if (dx or dy) and nation_of(lo, la) == n0:
                how += ', nudged %s km by the direction in its name' % k
            else:
                lo, la = lonlat
    rows.append(dict(d=q, label=L, desc=r.desc, admin=r.admin, lon=lo, lat=la, how=how))
G2 = pd.DataFrame(rows)
G2['nation'] = [nation_of(a, b) if a is not None and not pd.isna(a) else None for a, b in zip(G2.lon, G2.lat)]
if TEST:
    t = G2.merge(dd[['coord']], left_on='d', right_index=True)
    t = t[t.coord.map(lambda x: isinstance(x, str)) & t.lon.notna() & ~t.how.str.startswith('hand')]
    xy = t.coord.map(pt)
    t['err_km'] = [math.hypot((a - x[0]) * 111 * math.cos(math.radians(b)), (b - x[1]) * 111) for a, b, x in zip(t.lon, t.lat, xy)]
    print('fallback test on', len(t), 'items with their own coordinates: median error km', round(t.err_km.median(), 1), 'p90', round(t.err_km.quantile(.9), 1), 'share within 25 km', round((t.err_km < 25).mean(), 3))
    print(t.sort_values('err_km').tail(15)[['label', 'how', 'err_km']].to_string())
    json.dump({'n': len(t), 'median_km': round(t.err_km.median(), 1), 'p90_km': round(t.err_km.quantile(.9), 1), 'share_within_25km': round((t.err_km < 25).mean(), 3)}, open(WORK + 'geocode_test.json', 'w'))
    sys.exit()
G2['desc'] = G2.desc.fillna('').str.replace('\u2013', ' to ').str.replace('\u2014', ' ')
G2.to_csv(WORK + 'districts_geo.csv', index=False)
print(len(G2), G2.lon.isna().sum())
print(G2.how.fillna('NONE').str.extract(r'^(\w+[ :]?\w*)')[0].value_counts())
print(G2[G2.lon.isna()][['label', 'desc', 'admin']].to_string())
