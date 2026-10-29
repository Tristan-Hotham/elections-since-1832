"""header.png, the 1200 by 630 social card: 1832 and 2024 side by side."""
import sys
sys.path.insert(0, '/home/claude/hist/elections-since-1832/code')
from figlib import *
fig = plt.figure(figsize=(12, 6.3), dpi=100)
fig.text(.045, .80, 'Who won', fontproperties=DISP, size=66, color=FG, va='bottom')
fig.text(.045, .66, 'here?', fontproperties=DISP, size=66, color=HOT, va='bottom')
fig.text(.047, .52, 'Every UK general election since 1832,\non one map you can play through', family=SER, size=19, color=FG, va='top', linespacing=1.35)
fig.text(.047, .28, f"{R['n_elections']} elections  ·  {R['n_mps_elected']:,} seats filled", family=MONO, size=13, color=MUT)
fig.text(.047, .085, 'maps.tristanhotham.com/elections-since-1832', family=MONO, size=12, color=MUT)
for k, (e, x0) in enumerate([('1832', .45), ('2024', .72)]):
    ax = fig.add_axes([x0, .04, .27, .9]); land(ax); dots(ax, E.index(e), size=7.5); mapax(ax)
    ax.text(.08, .93, e, transform=ax.transAxes, fontproperties=DISP, size=30, color=FG)
fig.savefig(ROOT + '/header.png', dpi=100)
print('ok')
