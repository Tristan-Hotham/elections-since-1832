"""Shared matplotlib helpers for the header, paper and blog figures and the collage."""
import json, os, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
from pyproj import Transformer

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
FD = os.environ.get('FONT_DIR', '/tmp/claude-0/-home-claude/c232619d-81e0-53f3-9de6-41e973630753/scratchpad/fonts')
DISP = None
if os.path.isdir(FD):
    for f in ['FrauncesVar.ttf', 'IBMPlexMono-Regular.ttf', 'IBMPlexMono-Medium.ttf', 'SourceSerif4-Regular.ttf', 'SourceSerif4-Semibold.ttf', 'SourceSerif4-It.ttf']:
        if os.path.exists(os.path.join(FD, f)): fm.fontManager.addfont(os.path.join(FD, f))
    DISP = fm.FontProperties(fname=os.path.join(FD, 'FrauncesVar.ttf'), weight=900)
SER, MONO = 'Source Serif 4', 'IBM Plex Mono'
BG, FG, MUT, RULE, LAND, SEA, HOT = '#F3EFE4', '#1C1B18', '#66625A', '#D6D0C1', '#E2DBCB', '#F3EFE4', '#1F6B4A'
plt.rcParams.update({'font.family': SER, 'font.size': 13, 'axes.edgecolor': MUT, 'axes.labelcolor': FG, 'xtick.color': MUT, 'ytick.color': MUT,
                     'axes.spines.top': False, 'axes.spines.right': False, 'savefig.facecolor': BG, 'figure.facecolor': BG, 'axes.facecolor': BG})
R = json.load(open(os.path.join(ROOT, 'data', 'results.json')))
D = json.load(open(os.path.join(ROOT, 'data', 'page', 'dots.json')))
NAT = json.load(open(os.path.join(ROOT, 'data', 'nations.geojson')))
FAM = D['fams']; FI = {f[0]: i for i, f in enumerate(FAM)}
E = [e['name'] for e in D['elections']]
TR = Transformer.from_crs(4326, 27700, always_xy=True)
ORDER = ['LIB', 'LU', 'PEEL', 'IRN', 'SF', 'LAB', 'SNP', 'PC', 'GRN', 'OTH', 'SPK', 'REF', 'ULS', 'ALLY', 'CON']


def year_of(i):
    d = D['elections'][i]['date']
    return int(d[:4]) + (int(d[5:7]) - 1) / 12


def land(ax, fc=LAND, ec=None, lw=0.4):
    for f in NAT['features']:
        g = f['geometry']; polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
        for p in polys:
            x, y = TR.transform(*np.array(p[0]).T)
            ax.fill(x / 1000, y / 1000, fc=fc, ec=ec or fc, lw=lw, zorder=1)


def dots(ax, ei, size=7, highlight=None, edge=BG, alpha=1):
    el = D['elections'][ei]
    x, y = TR.transform(np.array(el['lon']), np.array(el['lat']))
    cols = [FAM[f][2] for f in el['f']]
    if highlight is not None:
        cols = [c if highlight(el, k) else '#CFC8B8' for k, c in enumerate(cols)]
        order = np.argsort([1 if highlight(el, k) else 0 for k in range(len(cols))])
    else:
        order = np.arange(len(cols))
    ax.scatter(x[order] / 1000, y[order] / 1000, s=size, c=np.array(cols)[order], lw=0.25, edgecolors=edge, zorder=3, alpha=alpha)


def mapax(ax, ireland=True):
    ax.set_aspect('equal'); ax.axis('off')
    ax.set_xlim(-200 if ireland else 60, 660); ax.set_ylim(0, 980)


def save(fig, path, dpi=200):
    fig.savefig(path, dpi=dpi, bbox_inches=None)
    plt.close(fig)
