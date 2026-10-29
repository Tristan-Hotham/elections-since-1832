"""Coastline and nation outlines for the page, the figures and nation assignment.

Nations of the UK: the simplified county outlines from the How Roman is your road? project
(ONS boundaries, OGL v3), dissolved to England, Wales, Scotland and Northern Ireland.
Ireland: Natural Earth admin 0 (public domain). Writes data/nations.geojson (simplified).
"""
import json, sys
from shapely.geometry import shape, mapping, box
from shapely.ops import unary_union
sys.path.insert(0, '/home/claude/hist/elections-since-1832/code')
from common import *

g = json.load(open('/home/claude/hist/bread-rolls/data/counties.geojson'))
parts = {}
for f in g['features']:
    parts.setdefault(f['properties']['nation'], []).append(shape(f['geometry']).buffer(0))
nat = {k: unary_union(v) for k, v in parts.items()}
ne = json.load(open('/home/claude/hist/_data3/ne/geojson/ne_10m_admin_0_countries.geojson'))
for f in ne['features']:
    if f['properties'].get('ADM0_A3') == 'IRL':
        nat['Ireland'] = shape(f['geometry']).buffer(0)
feats = []
for k in ['England', 'Wales', 'Scotland', 'Northern Ireland', 'Ireland']:
    s = nat[k].simplify(0.004, preserve_topology=True)
    s = s.buffer(0)
    geo = json.loads(json.dumps(mapping(s)), parse_float=lambda x: round(float(x), 3))
    feats.append({'type': 'Feature', 'properties': {'nation': k}, 'geometry': geo})
json.dump({'type': 'FeatureCollection', 'features': feats}, open(OUT + 'nations.geojson', 'w'), separators=(',', ':'))
print({k: round(nat[k].area, 2) for k in nat})
