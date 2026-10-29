"""Fill code/page_template.html from data/results.json to make index.html.
{{path.to.value}} and {{path|int}} placeholders take numbers from results.json; /*R*/ gets the
small summary the charts and the map use."""
import sys, re
sys.path.insert(0, '/home/claude/hist/elections-since-1832/code')
from common import *
from parties import FAMILIES

R = json.load(open(OUT + 'results.json'))
C = pd.read_csv(OUT + 'contests.csv', dtype={'election': str})
dates = [C[C.election == e].date.iloc[0] for e in ELECTIONS]
_p = load_parliament()
dates_end = [(_p[_p.gek == e].end.iloc[0] if (_p.gek == e).any() else '2024-07-04') for e in ELECTIONS]
R['validate_note'] = '%s%% of seats' % round(100 * 30651 / 31056, 1)   # replaced below from the live check
v = json.load(open(WORK + 'validate.json'))
R['geocode_pct'] = round(100 * R['geocode_test']['share_within_25km'])

# surname agreement, recomputed here so the page quotes the current figure
m, d = load_wikidata()
K = pd.read_csv(OUT + 'candidates.csv', dtype={'election': str})
mt = pd.read_csv(WORK + 'match.csv').set_index(['gek', 'con'])
def wsurn(label):
    if not isinstance(label, str): return ''
    w = norm(re.sub(r',.*$', '', re.sub(r'\(.*?\)', '', label))).split()
    return w[-1] if w else ''
wsur = m.dropna(subset=['d']).groupby(['gek', 'd']).personL.apply(lambda s: ' '.join(wsurn(x) for x in s)).to_dict()
agree = tot = 0
for r in K[K.elected & (K.election != '2024')].itertuples():
    q = mt.loc[(r.election, r.constituency)].d if (r.election, r.constituency) in mt.index else None
    if not isinstance(q, str): continue
    tot += 1
    s = norm(r.candidate.split(',')[0]).split()
    agree += bool(s) and any(x in wsur.get((r.election, q), '').split() for x in s)
R['surname_agreement'] = {'agree': agree, 'total': tot, 'pct': round(100 * agree / tot, 1)}
R['validate_note'] = '%s%% of the %s seats filled from 1832 to 2019' % (R['surname_agreement']['pct'], f"{tot:,}")
json.dump(R, open(OUT + 'results.json', 'w'), indent=1)

S = lambda e, f: R['seats_by_family'][e].get(f, 0)
tot = lambda e: R['seats'][e]
UK = [[49.9, -10.4], [58.9, 1.8]]
stories = [
    dict(t='1832', d='The first reformed Parliament', e='1832', b=UK, long=f"At the first election after the Reform Act the Whig and Liberal family won {S('1832','LIB')} of {tot('1832')} seats and the Tories {S('1832','CON')}. Pairs of dots are two-member seats. {R['uncontested']['1832']['seats']} seats had no contest."),
    dict(t='1859', d=f"{R['uncontested']['1859']['share']}% of seats unopposed", e='1859', mode='unc', b=UK, long=f"In 1859, {R['uncontested']['1859']['seats']} of {tot('1859')} seats were returned without a contest, the most of any election here. Coloured dots were unopposed."),
    dict(t='1906', d='The Liberal landslide', e='1906', b=UK, long=f"The Liberals won {S('1906','LIB')} seats, the Conservatives {S('1906','CON')} and their Liberal Unionist allies {S('1906','LU')}. The Labour Representation Committee won {S('1906','LAB')}."),
    dict(t='1918', d='Sinn Féin sweeps Ireland', e='1918', b=[[51.3, -10.7], [55.5, -5.3]], long=f"Sinn Féin won {R['ireland_1918']['sf']} of Ireland's {R['ireland_1918']['total']} seats; the Irish Parliamentary Party kept {R['ireland_1918']['irn']} there. Unionists held {R['ireland_1918']['con']}, mostly in the north east."),
    dict(t='1945', d="Labour's first majority", e='1945', b=UK, long=f"Labour won {S('1945','LAB')} of {tot('1945')} seats, its first majority. The Liberals were down to {S('1945','LIB')}."),
    dict(t='1951', d=f"{S('1951','LIB')} Liberals left", e='1951', b=UK, long=f"The Liberal family's low point: {S('1951','LIB')} seats, on {R['lib_vote']['1951']}% of the votes counted here."),
    dict(t='2015', d=f"SNP {R['scot']['2015']['snp']} of {R['scot']['2015']['total']}", e='2015', b=[[54.6, -7.7], [58.8, -0.7]], long=f"The SNP won {R['scot']['2015']['snp']} of Scotland's {R['scot']['2015']['total']} seats, on {R['scot_snp_vote_2015']}% of the Scottish vote. Labour, the Conservatives and the Liberal Democrats kept one each."),
    dict(t='2019', d='The Red Wall', e='2019', b=[[51.4, -5.3], [55.9, 0.3]], long=f"In the North, the Midlands and Wales, {R['redwall']['seats_2019']} seats that Labour won in 2017 went Conservative in 2019. Tap a dot to see how long Labour had held it."),
    dict(t='2024', d='Reform: votes and seats', e='2024', mode='share', fam='REF', b=UK, long=f"Reform UK won {R['ref_2024_vote']}% of the votes and {R['ref_2024_seats']} seats; Labour won {S('2024','LAB')} seats on {R['lab_2024_vote']}%. The map shades each seat by Reform's share."),
]
small = {k: R[k] for k in ['seats_by_family', 'vote_share_by_family', 'uncontested', 'turnout_median', 'nations', 'redwall']}
small.update(elections=ELECTIONS, dates=dates, dates_end=dates_end, fams=[list(f) for f in FAMILIES], nations_list=['England', 'Scotland', 'Wales', 'Ireland', 'Northern Ireland'], stories=stories)

T = open(ROOT + 'code/page_template.html').read()


def get(path):
    x = R
    for p in path.split('.'):
        x = x[int(p)] if isinstance(x, list) else x[p]
    return x


def fill(mo):
    path, _, f = mo.group(1).partition('|')
    v = get(path.strip())
    if f == 'int':
        return f"{int(round(v)):,}"
    return str(v)


T = re.sub(r'\{\{([^}]+)\}\}', fill, T)
T = T.replace('/*R*/', json.dumps(small, separators=(',', ':'), ensure_ascii=False))
open(ROOT + 'index.html', 'w').write(T)
print('index.html', len(T), R['surname_agreement'])
