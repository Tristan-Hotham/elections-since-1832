# Who won here? Every UK general election since 1832 on one map

Every United Kingdom general election from 1832 to 2024 on one map you can play through: who won each seat, vote shares, turnout and the seats nobody contested. Each seat is a dot (two-member seats two dots), coloured by party family, at a point for its constituency.

**Interactive version:** https://maps.tristanhotham.com/elections-since-1832/

**Paper:** https://doi.org/10.5281/zenodo.23761425

This repository holds the interactive page, the datasets, the computed results and the analysis code for a data study by Dr Tristan Hotham (Independent researcher).

## Headline results

- 49 general elections, 28,346 constituency contests, 89,545 candidacies and 31,736 seats filled, 1832 to 2024.
- From 1832 to 1880, 40.1% of seats were returned without a contest; in 1859 it was 380 seats (58.1%). The last unopposed returns at a general election were in 1951 (4 seats).
- In 1832, 505 of 658 seats were in constituencies returning two or more members; from 1832 to 1880, 33.9% of two-member returns split between two party families. The last multi-member seats were filled in 1945.
- The Whig, Liberal and Liberal Democrat family won 397 seats in 1906 and 6 in 1951. Labour first won seats in 1900, passed the Liberals in 1922 and won its first majority in 1945 (394 of 640).
- Wales returned 33 Liberals of 34 members in 1906 (with Monmouthshire); the Conservatives won no Welsh seat in 1906, 1997, 2001 and 2024. The SNP won 56 of 59 Scottish seats in 2015 and 9 of 57 in 2024. Sinn Féin won 73 of Ireland's 105 seats in 1918.
- Red Wall (defined here as seats in the North East, North West, Yorkshire and the Humber, the East and West Midlands and Wales that Labour won in 2017 and the Conservatives won in 2019): 45 seats. Of the 160 new seats in those regions that the Conservatives would have won in 2019 (notional results), Labour won 106 in 2024 and the Conservatives kept 42.
- In 2024 Labour won 63.2% of seats on 33.7% of the votes; Reform UK won 14.3% and 5 seats.

## Files

- `index.html`: the interactive page (map with year slider, winner, vote share, turnout and unopposed views, place search, "who won nearest here" strip, Map layers panel, charts). Loads `data/page/` and `data/nations.geojson`.
- `header.png`: social card (1200 by 630).
- `data/contests.csv`: one row per constituency contest (28,346 rows): election, polling start date, constituency, Wikidata item, seats, uncontested, number of candidates, turnout (as given), votes cast, display point (lon, lat) and nation.
- `data/candidates.csv`: one row per candidacy (89,545 rows): party label as in the source, party family, votes, share of votes cast in the contest, elected.
- `data/constituency_places.csv`: every constituency item with its point and where the point came from.
- `data/seats_by_family.csv`, `data/votes_by_family.csv`, `data/nations_by_family.csv`: summary tables.
- `data/results.json`: every number quoted on the page, in the paper, the blog post and the collage.
- `data/nations.geojson`: simplified outlines of England, Wales, Scotland, Northern Ireland and Ireland (map lines, nation assignment).
- `data/page/`: compact files for the page (`dots.json` with the spread dot positions for each election, `e00.json` to `e48.json` with candidates, `places.json` for search and place names).
- `code/`: the analysis, run in order (below). `code/parties.py` holds the party family rules with the reasons.
- `release/`: the paper (PDF, LaTeX source and figures), the blog post and figures, and the Zenodo files.
- `reddit/`: the collage, its script and the post text.

## How to rerun

The scripts read the source bundles in place (retrieved 29 October 2026; paths in `code/common.py`): the UK Parliament results file (`download.csv` from github.com/ukparliament/uk-general-elections), the Commons Library candidate files for 2010 to 2024 and the notional 2019 results, Wikidata query results (members, constituencies, places), the Wikipedia election infoboxes, OS Open Names, GeoNames cities15000, Natural Earth and the ONS county outlines used in earlier projects.

```
python3 code/01_match.py        # Parliament contests to Wikidata constituencies
python3 code/02_contests.py     # seats per constituency and winners
python3 code/03_geo.py          # nation outlines
python3 code/04_geocode.py      # a point for every constituency (add "test" to run the accuracy test)
python3 code/05_build.py        # clean tables, 2024, nations, notional 2019
python3 code/06_validate.py     # check seat totals against Wikipedia
python3 code/07_analyse.py      # results.json
python3 code/08_page_data.py    # page files and the spread dot layout
python3 code/09_build_site.py   # index.html from code/page_template.html
python3 code/10_header.py       # header.png
python3 code/11_figures.py      # paper and blog figures
python3 release/paper/build_paper.py
python3 release/build_release.py
```

It needs Python 3 with pandas, numpy, scipy, shapely, pyproj and matplotlib, and xelatex for the paper.

## Method in brief

- **Results**: candidate-level results 1832 to 2019 from UK Parliament; 2024 and notional 2019 (2024 boundaries) from the Commons Library.
- **Seats per constituency**: the number of members Wikidata records as elected for the constituency at that general election. Totals match the size of the House at every election (658 in 1832, 670 in 1885, 707 in 1918, 650 in 2024).
- **Winners**: top candidates by votes, or every candidate in an unopposed return. Winners' surnames agree with Wikidata's members for 98.7% of 31,056 seats (1832 to 2019).
- **Party families**: fifteen families (see `code/parties.py`); every candidate keeps the source's party label. Conservative, Liberal and Labour seat totals agree with the Wikipedia infobox within two seats in 111 of 130 comparisons; the larger gaps are grouping differences (Repeal and Whig members 1835 and 1837, Peelites, Independent Irish, the National Liberals of 1922 and of the 1950s).
- **Places**: 1,269 of 2,326 constituency items have Wikidata coordinates; the rest are placed at their town or county (Wikidata, OS Open Names) or at a named stand-in town (47); university seats at their university town. In a test on items with known coordinates, 97.7% of looked-up points were within 25 km (median error 1.3 km). On the page, dots are spread apart so none overlap.

## Known limits

- Points, not boundaries; county divisions are only roughly placed, and crowded areas are spread out.
- No by-elections and no changes of party between elections.
- Party families are my grouping; nineteenth-century labels follow the source.
- Vote shares count votes cast in contested seats; before 1950 electors in multi-member seats had more than one vote.
- Turnout before 2024 is the source's per-seat figure (median shown); electorates were only available for 2010 onwards.
- "Who won nearest here" uses the nearest constituency point, not the constituency that contained the spot.

## Sources and licences

- UK General Elections Results 1832 to 2019, UK Parliament (https://api.parliament.uk/uk-general-elections; data https://github.com/ukparliament/uk-general-elections): Open Parliament Licence v3.0.
- House of Commons Library, Election Results (https://electionresults.parliament.uk/): 2010 to 2024 candidate results and notional 2019 results on the 2024 boundaries (Rallings and Thrasher, Professor David Denver, Nicholas Whyte, for Sky News, PA, BBC News and ITV News): Open Parliament Licence v3.0.
- Wikidata: CC0. English Wikipedia (election infoboxes, used for the check): CC BY-SA 4.0.
- OS Open Names (contains OS data © Crown copyright and database right 2026) and ONS county boundaries: Open Government Licence v3.0. GeoNames: CC BY 4.0. Natural Earth: public domain.
- Base map and hill shading tiles: Esri.

The data in `data/` and the text of the page are released under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/). Election results contain Parliamentary information licensed under the Open Parliament Licence v3.0. The code (`code/`, `release/` scripts) is released under the MIT licence (see `LICENSE`).

## Related

- Rotten Boroughs: where are they now? https://maps.tristanhotham.com/rotten-boroughs/

## Citation

Hotham, T. (2026). Who Won Here? Every UK General Election since 1832 on One Map. Zenodo. https://doi.org/10.5281/zenodo.23761425

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
