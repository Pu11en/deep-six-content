# New Braunfels new neighborhoods: enriched and ranked

Date: 2026-10-16
File: `neighborhoods-ranked-2026-10-16.csv` (35 rows, one per neighborhood, ranked by total score)

Per Drew's change, this file has no hook angles or video ideas. It holds facts with sources, plus the scores.

## Method

1. Start list: `deep-six-factory/verticals/02-new-neighborhoods/outputs/leads.csv` (35 rows). Lot, permit and recording counts come from that file and from `data/good/*.json` (city and county permit and plat data). Neither was edited.
2. Location: city address GIS, the Census geocoder or the lead coordinates gave a center point and, where possible, a bounding box. County is taken from that data.
3. Land facts were looked up automatically for each point or box. All sources are free public APIs:
   - FEMA NFHL: whether a 100-yr flood zone (A/AE) touches the area.
   - USGS NHD: named creeks or rivers in or near the box.
   - USDA SSURGO soils: the soil map unit names. "Houston Black / Branyon / Heiden" are black shrink-swell clays. "Rumple-Comfort / Brackett-Rock outcrop / Real gravelly loam" are shallow rocky limestone.
4. Web research: free web search and page extraction only, with no accounts and no contact. Sources were builder pages, community sites, NewHomeSource/Zillow/Redfin, city/county/TCEQ/Comptroller documents (for MUD lists), news stories and Facebook search results.
5. Every fact has a source URL. If no source was found it says `unknown`. Anything inferred is marked "inferred" or "likely".

## Scoring (each 1-5, total out of 25)

- **Momentum** (people arriving in the next 6-12 months), based on permits plus homes finished in the last 90 days, and lots recorded in the last 12 months:
  - 5 = 40+ permits/finished, or 250+ lots recorded while under construction
  - 4 = 20+ permits/finished, or 150+ lots
  - 3 = 5+ permits/finished, or 50+ lots
  - 2 = paper stage with a known builder or some activity
  - 1 = paper only, nothing else known
  - Meyer Ranch was set to 4 by hand: it is established, with 200+ homesites open and 308 new lots filed.
- **Size** (planned homes; recorded lots if there is no plan total): 5 = 3,000+, 4 = 1,000+, 3 = 500+, 2 = 200+, 1 = under 200 or unknown.
- **Spend** (new-home price): 5 = about $1M, 4 = mostly $450k+, 3 = $300k-$450k, 2 = $250k-$330k or unknown (neutral), 1 = mostly under $300k (Lennar entry-level etc.).
- **Pest story**: one point for each documented feature, capped at 5. The features are: creek or river nearby; FEMA flood zone; rocky limestone soil; shrink-swell clay soil; wooded / Hill Country / ranch land in the marketing; lake or pond. It scores 1 if the location wasn't found.
- **Online presence**: 5 = own site plus active resident Facebook group plus news. 4 = site or HOA portal plus Facebook. 3 = own site or Facebook or news. 2 = builder pages only. 1 = government documents only or nothing.

No Reddit threads or Nextdoor pages turned up for any neighborhood through free search. Treat both as unknown, not as zero.

## Top 10

1. **Veramendi (23)**, Comal, NW NB between Hwy 46 and River Rd. About 6,000 units on 2,400 acres, with 43 permits and 17 homes finished in the last 90 days. Builders include Highland, Perry, Coventry, Beazer and Pulte, at about $360k-$925k. Blieders Creek and the Guadalupe River are nearby, FEMA A/AE zones touch the area, and the soil is rubbly limestone. There are 480 acres of parks, an active Facebook group and the city's WID.
2. **Mayfair (22)**, Comal, north NB on I-35. About 6,000 units on 1,900 acres, with 25 permits and 38 finished in the last 90 days. Prices run from the high $300s to about $800k (Perry, Toll, Coventry, Highland). It has a signature lake, 35 miles of trails and 300+ acres of parks, on black clay with Mesquite and Water Hole creeks nearby. Has a "Mayfair Neighbors" Facebook group.
3. **Meyer Ranch (21)**, Comal, Hwy 46 west toward Canyon Lake. A 700-acre former cattle ranch with 200+ homesites open and new units for 308 more lots filed. Prices run about $374k-$714k (Chesmar, Weekley, DRB, Scott Felder). The soil is rock-outcrop limestone near Dry Comal Creek. It has a resort pool, trails, a dog park, a resident Facebook group and a MUD.
4. **Sky Ranch (16)**, Guadalupe, east NB. 1,247 planned lots, with 459 recorded in 2026 alone. Lennar only, $189k-$307k. Alligator Creek is nearby, an AE flood zone touches the area and the soil is black clay. Has a Sky Ranch MUD and lifeatskyranch.com.
5. **Sunflower Ridge (15)**, Comal, off I-35 near Creekside. 363 lots recorded. Builders are Highland, Coventry, DRB and Brightland, from about $305k-$370k. Alligator Creek and an AE zone are nearby. It has an HOA portal and a community site.
6. **Kyndwood (14)**, Comal, north NB beside Mayfair. 1,052 planned lots, with 153 recorded in the last 12 months. Lennar, $217k-$329k. Water Hole Creek, an A zone and clay soil. Kyndwood MUD. Online presence is weak.
7. **Park Place (14)**, Guadalupe, south NB off Zipp Rd. 760 planned lots and 36 permits in the last 90 days. M/I, Century and First America, from the high $200s. Long Creek is nearby and the soil includes Tinn clay "frequently flooded". Park Place MUD.
8. **Parkside (14)**, Guadalupe, SE NB. 929 planned lots, with 258 recorded in the last 12 months. Lennar, $238k-$314k. It has a pool and trail, black clay soil and an A zone. Active HOA site and a 232-member Facebook group.
9. **Preserve at Elm Creek (14)**, Comal, far west Hill Country. About 107 lots on 1-acre "heavily wooded" lots. Perry and Grand Endeavor, $995k-$1.4M. Elm, Little Bear and Tausch creeks are nearby, and the soil is rubbly limestone. Small, but the highest spend.
10. **Clear Spring Meadows (13)**, Guadalupe, east NB at Hwy 46 / FM 758. 25 permits and 18 finished in the last 90 days. M/I and Centex, from $223k. The Guadalupe River and an A zone are nearby. No community site found.

Ranks 11-15, all at 13: South Point (KB Legend Heights, inferred), Kraft, The Landing, Clear Creek (next to Lake Dunlap, AE zone) and Purlsong (about 1,900 homes planned, early, with flood concerns in the news).

## Data gaps

- 3 of 35 are full, 21 partial and 11 minimal (see the `enrichment_level` column). "Full" means builder, price, amenities, HOA/MUD and planned total are all sourced.
- Most "Section in review" items have no builder, price or web presence yet: Windstone, Trinity Grove, Blackwell, Liberty Trails, The Silos, Kohlenberg, Hueco Springs Ranch and Westridge. Their scores are mostly paper-stage guesses.
- Colina Ranch and Autumn Ridge were not geocoded, so their land facts are unknown. Their size is a 50/50 split of the ~1,259 water connections that GVSUD gave for both together.
- Kraft, Wunderlich, Laubach and Hilltop Meadows appear to be sections of Lennar's Voss Farms, and The Landing a section of Sky Ranch. This is inferred from street names and listings. Confirm it before running separate ads.
- Steelwood Trail: the county field disagrees between sources (city GIS says Comal; the MUD list and ETJ say Guadalupe).
- Homes actually built or occupied are unknown everywhere. Only recorded lots and 90-day permit counts exist.
- No Reddit or Nextdoor data. Facebook was checked only through search results; no logged-in browsing was done.
- The FEMA, NHD and soil results use one point or bounding box per neighborhood, so they are approximate. "Nearby" for streams means within about 0.5-1 km of the box.
