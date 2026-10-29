"""Reddit collage: all 49 general elections as small dot maps, with headline numbers. 2400 x 3000 px."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'code'))
from figlib import *
RW = R['redwall']
fig = plt.figure(figsize=(12, 15), dpi=200)
fig.text(.05, .968, 'Who won here?', fontproperties=DISP, size=54, color=FG, va='top')
fig.text(.05, .902, f"Every UK general election since 1832, {R['n_elections']} in all. Each dot is a seat,", family=SER, size=19, color=FG, va='top')
fig.text(.05, .881, 'coloured by the party family that won it. Two-member seats are two dots.', family=SER, size=19, color=FG, va='top')
# legend
leg = [('LIB', 'Whig, Liberal, Lib Dem'), ('CON', 'Conservative and Unionist'), ('LAB', 'Labour'), ('IRN', 'Irish nationalist'), ('SF', 'Sinn Féin'),
       ('SNP', 'SNP'), ('LU', 'Liberal Unionist'), ('ULS', 'Ulster unionist'), ('PC', 'Plaid Cymru'), ('OTH', 'Others')]
x, y = .05, .846
for f, lab in leg:
    w = .025 + len(lab) * .0082
    if x + w > .97: x, y = .05, y - .018
    fig.text(x, y, '●', color=FAM[FI[f]][2], size=15, va='center', family='DejaVu Sans')
    fig.text(x + .017, y, lab, color=FG, size=11.5, va='center', family=MONO); x += w + .012
# grid of maps
cols, rows = 7, 7
gx0, gx1, gy0, gy1 = .02, .98, .30, .822
cw, ch = (gx1 - gx0) / cols, (gy1 - gy0) / rows
for i, e in enumerate(E):
    r, c = divmod(i, cols)
    ax = fig.add_axes([gx0 + c * cw, gy1 - (r + 1) * ch, cw, ch * .9])
    land(ax, fc='#E4DDCC'); dots(ax, i, size=1.9, edge='none'); mapax(ax)
    lab = e.replace('January ', 'Jan ').replace('December ', 'Dec ').replace('February ', 'Feb ').replace('October ', 'Oct ')
    ax.text(.04, .9, lab, transform=ax.transAxes, fontproperties=DISP, size=13.5 if len(lab) <= 4 else 11.5, color=FG, va='top')
# big numbers
nums = [
    (f"{R['unc_max']['share']}%", f"of seats in {R['unc_max']['election']} were filled\nwith no contest at all.\nThe last: {R['unc_last']['election']}", HOT),
    (f"{R['lib']['1906']} to {R['lib']['1951']}", 'Liberal family seats,\n1906 to 1951, as Labour\nrose to replace them', FAM[FI['LIB']][2]),
    (f"{R['scot']['2015']['snp']} of {R['scot']['2015']['total']}", "Scottish seats won by the\nSNP in 2015. In 2024:\n" + f"SNP {R['scot']['2024']['snp']}, Labour {R['scot']['2024']['lab']}", '#C9A400'),
    (f"{RW['of_which_2024']['LAB']} of {RW['notional_con_2019_area_2024seats']}", "notional 2019 Tory seats\nin the North, Midlands and\nWales won by Labour in 2024", FAM[FI['LAB']][2]),
]
for k, (big, small, col) in enumerate(nums):
    x0 = .05 + k * .235
    fig.text(x0, .285, big, fontproperties=DISP, size=33, color=col, va='top')
    fig.text(x0, .243, small, family=MONO, size=11.2, color=FG, va='top', linespacing=1.35)
# seat share strip
ax = fig.add_axes([.05, .117, .9, .05])
for i, e in enumerate(E):
    sh = R['seats_by_family'][e]; tot = sum(sh.values()); acc = 0
    for f in ORDER:
        v = sh.get(f, 0)
        if v: ax.bar(i, v / tot, bottom=acc, width=.86, color=FAM[FI[f]][2], lw=0); acc += v / tot
ax.set_xlim(-.6, len(E) - .4); ax.set_ylim(0, 1); ax.axis('off')
fig.text(.05, .175, 'Share of seats by party family, every election 1832 to 2024', family=MONO, size=11.5, color=MUT)
for i, e in [(0, '1832'), (E.index('1885'), '1885'), (E.index('1918'), '1918'), (E.index('1950'), '1950'), (E.index('1983'), '1983'), (len(E) - 1, '2024')]:
    fig.text(.05 + .9 * (i + .5) / len(E), .110, e, family=MONO, size=10.5, color=MUT, ha='center', va='top')
fig.text(.05, .078, 'Data: UK General Elections Results 1832 to 2019, UK Parliament; House of Commons Library Election Results (2024, notional 2019);\nOpen Parliament Licence v3.0. Members per seat and constituency points: Wikidata (CC0). Places: OS Open Names (OGL v3), Natural Earth.',
         family=MONO, size=9.6, color=MUT, va='top', linespacing=1.5)
fig.text(.05, .038, 'Dots are constituency points spread apart, not boundaries. Analysis and chart: Tristan Hotham, with Python and matplotlib.',
         family=MONO, size=9.6, color=FG, va='top')
fig.text(.05, .012, 'Interactive map: maps.tristanhotham.com/elections-since-1832', family=MONO, size=11, color=HOT, va='bottom', weight='medium')
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'every_election_since_1832.png')
fig.savefig(out, dpi=200)
print(out)
