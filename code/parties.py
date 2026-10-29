"""Party families used for colours and long-run counts.

The source keeps each candidate's own label (Whig, Liberal, Radicals, Liberal Unionist, ...).
Families group labels that sat together in the Commons. Choices that need judgement:
- Whigs, Radicals, Liberals, Lib-Labs, coupon Liberals (1918) and Lloyd George's National
  Liberals (1922) are in the Liberal family; so are the SDP, the Alliance and the Liberal
  Democrats, as the Liberal tradition's successors.
- The Liberal Nationals (1931 on, later National Liberals) sat with the Conservatives; they,
  National Labour, "National Government" candidates and the 1924 Constitutionalists form a
  separate "Conservative allies" family, not the Liberal family.
- Liberal Unionists (1886 to 1910) keep their own family; they merged with the Conservatives in 1912.
- Peelites (1847 to 1859) keep their own family.
- Irish Unionists before 1922 and Ulster Unionists up to 1970 took the Conservative whip, so
  they are in the Conservative family; from February 1974 the Ulster unionist parties (UUP, DUP,
  Vanguard and others) are their own family.
- Repeal, Independent Irish, Home Rule, Irish Parliamentary, Parnellite and anti-Parnellite
  members, the SDLP and similar are "Irish nationalist"; Sinn Fein is its own family.
"""

FAMILIES = [
    # code, label, colour (light theme)
    ('CON', 'Conservative and Unionist', '#2f5d9e'),
    ('LU', 'Liberal Unionist', '#7fa7d6'),
    ('PEEL', 'Peelite', '#5f9e9a'),
    ('ALLY', 'Liberal National and other Conservative allies', '#8a83c2'),
    ('LIB', 'Whig, Liberal and Liberal Democrat', '#e8a21a'),
    ('LAB', 'Labour', '#c8313a'),
    ('IRN', 'Irish nationalist', '#3d8b3d'),
    ('SF', 'Sinn Fein', '#1f5e3a'),
    ('SNP', 'SNP', '#f0d43a'),
    ('PC', 'Plaid Cymru', '#2aa889'),
    ('ULS', 'Ulster unionist parties (from 1974)', '#7b4a8f'),
    ('REF', 'UKIP, Brexit Party and Reform UK', '#22b6c9'),
    ('GRN', 'Green', '#9bc53d'),
    ('SPK', 'Speaker', '#8c8c8c'),
    ('OTH', 'Independents and others', '#b9a58b'),
]
FAM_LABEL = {c: l for c, l, _ in FAMILIES}
FAM_COLOUR = {c: k for c, _, k in FAMILIES}

POST1988 = {'1992', '1997', '2001', '2005', '2010', '2015', '2017', '2019', '2024'}
LATE = {'February 1974', 'October 1974', '1979', '1983', '1987', '1992', '1997', '2001', '2005', '2010', '2015', '2017', '2019', '2024'}

EXACT = {
    'Conservative': 'CON', 'Tory': 'CON', 'Unionist': 'CON', 'Scottish Unionist': 'CON', 'Unionist with Coalition Coupon': 'CON',
    'Scottish Unionist with Coalition Coupon': 'CON', 'Irish Unionist': 'CON', 'Irish Conservative': 'CON', 'Liberal-Conservative': 'CON',
    'Independent Conservative': 'CON', "St George's, Hanover Square, Independent Conservative Association": 'CON', 'Labour Unionist': 'CON',
    'Liberal Unionist': 'LU', 'Liberal Unionist and Crofters': 'LU',
    'Peelite': 'PEEL',
    'Liberal National': 'ALLY', 'National Liberal and Conservative': 'ALLY', 'Conservative and National Liberal': 'ALLY',
    'National Labour': 'ALLY', 'National Government': 'ALLY', 'Constitutionalist': 'ALLY',
    'Whig': 'LIB', 'Liberal': 'LIB', 'Radicals': 'LIB', 'Liberal-Labour': 'LIB', 'Liberal with Coalition Coupon': 'LIB',
    'Independent Liberal': 'LIB', 'Liberal and Crofters': 'LIB', 'Independent Liberal and Crofters': 'LIB', 'Liberal (Local)': 'LIB',
    'Independent Liberal-Labour': 'LIB', 'Liberal Democrats': 'LIB', 'Liberal Democrat': 'LIB', 'Social Democratic': 'LIB', 'SDP-Liberal Alliance': 'LIB',
    'Labour': 'LAB', 'Labour Co-op': 'LAB', 'Labour Co-Op': 'LAB', 'Labour Representation Committee': 'LAB', 'Co-operative': 'LAB',
    'Labour with Coalition Coupon': 'LAB', 'Coalition Labour': 'OTH',
    'Repeal Association': 'IRN', 'Repeal Association and Whig': 'IRN', 'Irish Confederation': 'IRN', 'Independent Irish': 'IRN',
    'Home Rule League': 'IRN', 'Home Rule League (Parnellite)': 'IRN', 'Irish Parliamentary': 'IRN', 'Irish National Federation': 'IRN',
    'Irish National League': 'IRN', 'Healyite Nationalist': 'IRN', 'All-for-Ireland': 'IRN', 'Irish Nationalist': 'IRN',
    'Independent Nationalist': 'IRN', 'Nationalist Party of Northern Ireland': 'IRN', 'SDLP': 'IRN', 'Social Democratic and Labour Party': 'IRN',
    'Social Democratic & Labour Party': 'IRN', 'Republican Labour': 'IRN', 'Unity': 'IRN', 'Independent Republican': 'IRN', 'Irish Labour': 'IRN',
    'Sinn Féin': 'SF', 'Sinn Fein': 'SF',
    'SNP': 'SNP', 'Scottish National Party': 'SNP',
    'Plaid Cymru': 'PC',
    'DUP': 'ULS', 'Democratic Unionist Party': 'ULS', 'Vanguard': 'ULS', 'UK Unionist': 'ULS', 'Ulster Popular Unionist': 'ULS',
    'Protestant Unionist': 'ULS', 'United Ulster Unionist': 'ULS', 'Russellite Unionist': 'ULS', 'Independent Unionist': 'ULS',
    'Traditional Unionist Voice': 'ULS',
    'UKIP': 'REF', 'UK Independence Party': 'REF', 'Brexit': 'REF', 'The Brexit Party': 'REF', 'Reform UK': 'REF',
    'Greens': 'GRN', 'Green': 'GRN', 'Green Party': 'GRN', 'Scottish Greens': 'GRN', 'Scottish Green Party': 'GRN',
    'Speaker': 'SPK', 'Speaker with Coalition Coupon': 'SPK',
}


def family(party, election, irish=True):
    p = str(party).strip()
    if p == 'National Liberal':
        return 'LIB' if election in ('1922',) else 'ALLY'
    if p in ('UUP', 'Ulster Unionist Party'):
        return 'ULS' if election in LATE else 'CON'
    if p in ('Liberal', 'Social Democratic', 'Social Democratic Party') and election in POST1988:
        return 'OTH'   # the continuing Liberal Party and SDP after the 1988 merger
    if p == 'Independent Unionist' and not irish:
        return 'CON'
    if p in EXACT:
        return EXACT[p]
    if p.startswith('Speaker'):
        return 'SPK'
    return 'OTH'
