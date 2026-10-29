"""Turn a constituency name into place-name candidates for geocoding (most specific first)."""
import re
DIRS = r'(North|South|East|West|Central|Mid|Middle|North East|North West|South East|South West|Northern|Southern|Eastern|Western|Inner|Outer|Upper|Lower)'
DROP = r'\b(Boroughs|Borough|Burghs|District of|District|Division|Universities|University|Town|City of|Cities of|The)\b'


def candidates(name):
    s = name.replace('&', 'and')
    s = re.sub(r'\(.*?\)', '', s).strip()
    out = []
    # split on " and " / commas into parts; keep the first part as main place
    parts = [p.strip() for p in re.split(r',| and ', s) if p.strip()]
    for p in [s] + parts:
        q = re.sub(DROP, '', p)
        q = re.sub(r'^(' + DIRS + r' )+', '', q.strip())
        q = re.sub(r'( ' + DIRS + r')+$', '', q.strip())
        q = re.sub(r'\s+', ' ', q).strip(' -')
        # "Liverpool Toxteth" -> try "Toxteth" then "Liverpool"
        w = q.split()
        KEEP = ('St', 'St.', 'Saint', 'Great', 'Little', 'New', 'Old', 'Kings', "King's", 'Market', 'High', 'Long', 'Isle', 'Isles', 'Forest', 'Castle')
        if len(w) >= 2 and w[0] not in KEEP and not w[1] in ('upon', 'on', 'under', 'of', 'le', 'in'):
            out += [q, ' '.join(w[1:]), w[0]]
        elif q:
            out.append(q)
    seen = []
    for o in out:
        if o and o not in seen and len(o) > 2:
            seen.append(o)
    return seen


def direction(name):
    """Unit offset (dx east, dy north) implied by direction words in the name."""
    n = ' ' + name + ' '
    dx = dy = 0
    if re.search(r'\b(North|Northern)\b', n): dy += 1
    if re.search(r'\b(South|Southern)\b', n): dy -= 1
    if re.search(r'\b(East|Eastern)\b', n): dx += 1
    if re.search(r'\b(West|Western)\b', n): dx -= 1
    return dx, dy
