# Reddit post

## Title

[OC] Every UK general election since 1832 as a dot map, one dot per seat: 49 elections, 31,736 seats filled

## Body

I mapped every UK general election from the 1832 Reform Act to 2024, with each seat as a dot coloured by the party family that won it (two-member seats are two dots). A few things stood out. Elections often were not contested at all: in 1859, 58.1% of seats were filled with no vote, and the last unopposed seats came in 1951. The Liberal family fell from 397 seats in 1906 to 6 in 1951. Of the 160 new seats in the North, Midlands and Wales that the Conservatives would have won in 2019 (notional results), Labour won 106 in 2024. Caveat: historic boundaries are not open data, so each seat is a point (spread apart so dots do not overlap), not an area. Interactive version, with a "who won near me since 1832" strip: https://maps.tristanhotham.com/elections-since-1832/

## Source comment

Source: UK General Elections Results 1832 to 2019, UK Parliament (candidate-level results, github.com/ukparliament/uk-general-elections), and House of Commons Library Election Results (2024 results and notional 2019 results on the 2024 boundaries), both Open Parliament Licence v3.0; Wikidata (members elected per seat at each election, constituency coordinates, CC0); OS Open Names (Open Government Licence v3.0); GeoNames (CC BY 4.0); Natural Earth (public domain). Seat totals checked against Wikipedia's election articles (CC BY-SA 4.0).

Tools: Python (pandas, numpy, scipy, shapely, pyproj, matplotlib), Leaflet for the interactive map.

Interactive map: https://maps.tristanhotham.com/elections-since-1832/
Blog post: https://blog.tristanhotham.com/2026/10/29/elections-since-1832/
Paper: https://doi.org/10.5281/zenodo.23761425
