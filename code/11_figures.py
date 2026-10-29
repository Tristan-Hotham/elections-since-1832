"""Static figures for the blog (release/blog/b_*.png, 1520 px wide) and the paper (release/paper/fig*.png)."""
import sys
sys.path.insert(0, '/home/claude/hist/elections-since-1832/code')
from figlib import *
B = ROOT + '/release/blog/'; P = ROOT + '/release/paper/'
YRS = [year_of(i) for i in range(len(E))]
famc = lambda f: FAM[FI[f]][2]
famn = lambda f: FAM[FI[f]][1]


def four_maps(path, w, h, dpi, title_size=26):
    fig = plt.figure(figsize=(w, h), dpi=dpi)
    for k, e in enumerate(['1832', '1906', '1945', '2024']):
        ax = fig.add_axes([k * .25, .0, .25, .88]); land(ax); dots(ax, E.index(e), size=5 if w < 9 else 9); mapax(ax)
        ax.text(.5, 1.0, e, transform=ax.transAxes, ha='center', va='bottom', fontproperties=DISP, size=title_size, color=FG)
    save(fig, path, dpi)


def legend_row(fig, fams, y, size=11, x0=.06, step=None):
    x = x0
    for f in fams:
        fig.text(x, y, '●', color=famc(f), size=size + 3, va='center', family=MONO)
        t = fig.text(x + .016, y, famn(f), size=size, va='center', family=MONO, color=FG)
        x += step or (.03 + len(famn(f)) * .0068 * size / 11)


def seats_chart(path, w, h, dpi, fs=12):
    fig = plt.figure(figsize=(w, h), dpi=dpi); ax = fig.add_axes([.07, .2, .91, .76])
    for i, e in enumerate(E):
        s = R['seats_by_family'][e]; tot = sum(s.values()); acc = 0
        for f in ORDER:
            v = s.get(f, 0)
            if v:
                ax.bar(YRS[i], v / tot * 100, bottom=acc, width=1.8, color=famc(f), lw=0); acc += v / tot * 100
    ax.axhline(50, color=BG, lw=1.2, ls=(0, (3, 3)))
    ax.set_xlim(1829, 2027); ax.set_ylim(0, 100); ax.set_yticks([0, 25, 50, 75, 100]); ax.set_yticklabels([f'{v}%' for v in [0, 25, 50, 75, 100]], family=MONO, size=fs)
    ax.set_xticks(range(1840, 2030, 20)); ax.set_xticklabels(range(1840, 2030, 20), family=MONO, size=fs)
    ax.spines['left'].set_visible(False); ax.tick_params(length=0)
    fams = ['LIB', 'CON', 'LU', 'PEEL', 'ALLY', 'LAB', 'IRN', 'SF', 'SNP', 'ULS', 'OTH']
    short = {'LIB': 'Whig, Liberal, Lib Dem', 'CON': 'Conservative and Unionist', 'LU': 'Liberal Unionist', 'PEEL': 'Peelite', 'ALLY': 'Liberal National and allies', 'LAB': 'Labour', 'IRN': 'Irish nationalist', 'SF': 'Sinn Féin', 'SNP': 'SNP', 'ULS': 'Ulster unionist (from 1974)', 'OTH': 'Others'}
    x, y = .07, .085
    for f in fams:
        lab = short[f]; wv = (.022 + len(lab) * .0071 * fs / 12) * 15.2 / w
        if x + wv > .99: x, y = .07, y - .05
        fig.text(x, y, '■', color=famc(f), size=fs + 2, va='center', family='DejaVu Sans'); fig.text(x + .014 * 15.2 / w, y, lab, size=fs - 1, va='center', family=MONO, color=FG); x += wv
    save(fig, path, dpi)


def votes_chart(path, w, h, dpi, fs=12):
    fig = plt.figure(figsize=(w, h), dpi=dpi); ax = fig.add_axes([.07, .12, .78, .84])
    labs = []
    for f, lab in [('CON', 'Conservative'), ('LIB', 'Liberal family'), ('LAB', 'Labour'), ('REF', 'UKIP and Reform')]:
        xs, ys = [], []
        for i, e in enumerate(E):
            v = R['vote_share_by_family'][e].get(f)
            if v is None: continue
            if f == 'REF' and v < .5: continue
            xs.append(YRS[i]); ys.append(v)
        ax.plot(xs, ys, color=famc(f), lw=2.6, marker='o', ms=4.5, mec=BG, mew=.8)
        labs.append([ys[-1], lab, famc(f), xs[-1]])
    labs.sort()
    for k in range(1, len(labs)):
        if labs[k][0] - labs[k - 1][0] < 3.2: labs[k][0] = labs[k - 1][0] + 3.2
    for y, lab, c, x in labs:
        ax.text(x + 2, y, lab, color=c, size=fs, va='center', family=MONO, weight='medium')
    ax.set_xlim(1829, 2027); ax.set_ylim(0, 70); ax.set_yticks(range(0, 71, 10)); ax.set_yticklabels([f'{v}%' for v in range(0, 71, 10)], family=MONO, size=fs)
    ax.set_xticks(range(1840, 2030, 20)); ax.set_xticklabels(range(1840, 2030, 20), family=MONO, size=fs); ax.grid(axis='y', color=RULE, lw=.8); ax.set_axisbelow(True)
    ax.spines['left'].set_visible(False); ax.tick_params(length=0)
    save(fig, path, dpi)


def unc_chart(path, w, h, dpi, fs=12):
    fig = plt.figure(figsize=(w, h), dpi=dpi); ax = fig.add_axes([.07, .13, .91, .83])
    v = [R['uncontested'][e]['share'] for e in E]
    ax.bar(YRS, v, width=1.8, color=HOT, lw=0)
    i = E.index(R['unc_max']['election']); ax.text(YRS[i] + 1.5, v[i] + 1, f"{R['unc_max']['election']}: {v[i]}%", size=fs, family=MONO, weight='medium')
    j = E.index(R['unc_last']['election']); ax.text(YRS[j] + 1.5, v[j] + 3, f"last: {E[j]}, {R['unc_last']['seats']} seats", size=fs, family=MONO)
    ax.set_xlim(1829, 2027); ax.set_ylim(0, 65); ax.set_yticks(range(0, 61, 20)); ax.set_yticklabels([f'{v}%' for v in range(0, 61, 20)], family=MONO, size=fs)
    ax.set_xticks(range(1840, 2030, 20)); ax.set_xticklabels(range(1840, 2030, 20), family=MONO, size=fs); ax.grid(axis='y', color=RULE, lw=.8); ax.set_axisbelow(True)
    ax.spines['left'].set_visible(False); ax.tick_params(length=0)
    save(fig, path, dpi)


def nations_chart(path, w, h, dpi, fs=12):
    fig = plt.figure(figsize=(w, h), dpi=dpi)
    for k, (key, title) in enumerate([('Scotland', 'Scotland'), ('Wales', 'Wales (with Monmouthshire)')]):
        ax = fig.add_axes([.07, .56 - k * .47, .91, .36])
        for i, e in enumerate(E):
            s = R['nations'][key].get(e)
            if not s: continue
            tot = sum(s.values()); acc = 0
            for f in ORDER:
                v = s.get(f, 0)
                if v: ax.bar(YRS[i], v / tot * 100, bottom=acc, width=1.8, color=famc(f), lw=0); acc += v / tot * 100
        ax.set_xlim(1829, 2027); ax.set_ylim(0, 100); ax.set_yticks([0, 50, 100]); ax.set_yticklabels(['0%', '50%', '100%'], family=MONO, size=fs)
        ax.set_xticks(range(1840, 2030, 20)); ax.set_xticklabels(range(1840, 2030, 20), family=MONO, size=fs); ax.spines['left'].set_visible(False); ax.tick_params(length=0)
        ax.text(0, 1.06, title, transform=ax.transAxes, fontproperties=DISP, size=fs + 8)
    save(fig, path, dpi)


def redwall_map(path, w, h, dpi, fs=12):
    rw = set(open(ROOT + '/work/redwall_2019.txt').read().split('\n'))
    fig = plt.figure(figsize=(w, h), dpi=dpi)
    ax = fig.add_axes([0, 0, .55, 1]); land(ax)
    hl = lambda el, k: el['contests'][el['c'][k]][0] in rw
    dots(ax, E.index('2019'), size=16, highlight=hl); ax.set_aspect('equal'); ax.axis('off'); ax.set_xlim(150, 660); ax.set_ylim(150, 680)
    ax2 = fig.add_axes([.62, .18, .34, .6])
    rows = sorted(R['redwall']['of_which_2024'].items(), key=lambda t: -t[1])
    names = {'LAB': 'Labour', 'CON': 'Conservative', 'LIB': 'Lib Dem', 'REF': 'Reform UK', 'PC': 'Plaid Cymru', 'GRN': 'Green'}
    ax2.barh(range(len(rows)), [v for _, v in rows], color=[famc(f) for f, _ in rows], height=.7)
    for i, (f, v) in enumerate(rows): ax2.text(v + 2, i, str(v), va='center', family=MONO, size=fs, weight='medium')
    ax2.set_yticks(range(len(rows))); ax2.set_yticklabels([names[f] for f, _ in rows], family=MONO, size=fs); ax2.invert_yaxis(); ax2.set_xticks([]); ax2.spines['bottom'].set_visible(False); ax2.spines['left'].set_visible(False); ax2.tick_params(length=0)
    ax2.text(0, 1.1, f"2024 winners of the {R['redwall']['notional_con_2019_area_2024seats']}\nnotional 2019 Conservative seats", transform=ax2.transAxes, family=MONO, size=fs, va='bottom')
    ax.text(.04, .97, f"{R['redwall']['seats_2019']} seats Labour won in 2017\nand lost to the Conservatives in 2019", transform=ax.transAxes, family=MONO, size=fs, va='top', color=FG)
    save(fig, path, dpi)


# blog, 1520 px wide
four_maps(B + 'b_maps.png', 15.2, 5.6, 100, 30)
seats_chart(B + 'b_seats.png', 15.2, 7.6, 100, 14)
votes_chart(B + 'b_votes.png', 15.2, 7.0, 100, 14)
unc_chart(B + 'b_unopposed.png', 15.2, 6.0, 100, 14)
nations_chart(B + 'b_nations.png', 15.2, 8.6, 100, 14)
redwall_map(B + 'b_redwall.png', 15.2, 8.4, 100, 14)
# paper (print, 300 dpi)
four_maps(P + 'fig1_maps.png', 7.2, 2.7, 300, 14)
seats_chart(P + 'fig2_seats.png', 7.2, 4.2, 300, 8)
votes_chart(P + 'fig3_votes.png', 7.2, 3.6, 300, 8)
unc_chart(P + 'fig4_unopposed.png', 7.2, 3.0, 300, 8)
nations_chart(P + 'fig5_nations.png', 7.2, 4.6, 300, 8)
redwall_map(P + 'fig6_redwall.png', 7.2, 4.0, 300, 8)
print('done')
