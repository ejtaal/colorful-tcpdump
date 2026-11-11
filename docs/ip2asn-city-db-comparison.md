# DB-IP City Lite vs GeoLite2-City — comparison report

*Analysis date: 2026-11-11. Data versions: `data/dbip-city-lite-2026-11.mmdb` (DB-IP
City Lite, monthly release) and `data/GeoLite2-City.mmdb` (MaxMind GeoLite2-City),
both read locally via `maxminddb`. Reproduce with `docs/analyze-city-dbs.py`
(run from the repo root, e.g. `.venv/bin/python docs/analyze-city-dbs.py`).*

## Why this comparison exists

`ip2asn-combined.tsv` (iptoasn.com) provides country + ASN only, so city-level
info for CTD comes from a separate city mmdb. Two free candidates:

| | DB-IP City Lite | GeoLite2-City |
|---|---|---|
| License | CC BY 4.0, freely redistributable (with attribution) | MaxMind license, **redistribution forbidden** |
| Access | public download URL, no account | requires free MaxMind account + license key |
| Update cadence | monthly | ~every 2 days |

Both are loaded by `data/ip2asn_lookup.py` (newest file by mtime wins, `.gz`
auto-decompressed), so the question is purely which one should be the primary.

## Methodology

- Sample IPs uniformly at random over all 579,453 *routed* ranges in
  `ip2asn-combined.tsv` (ASN known, country known).
- Run 1: 12 IPs hand-checked, then 3,000 IPs. Run 2: **1,000,000 IPs**
  (793,104 v4 / 206,896 v6; seed 1234, ~55 s runtime).
- Lookups are plain mmdb gets; distances between coordinate answers use the
  haversine formula.
- Caveat: sampling is uniform over *ranges*, not over real traffic. Small
  hosting /24s are therefore over-represented relative to consumer ISP space,
  which slightly favors the "cloud/datacenter" view of the world. It also
  matches how traceroute targets tend to look, which is what CTD is for.

## Coverage (1,000,000 IPs)

| metric | DB-IP | GeoLite2-City |
|---|---|---|
| has country | 100% | 99.9% |
| has region/state | **98.7%** | 44.0% |
| has **city** | **100%** | **43.8%** |
| has lat/lon | 100% | 99.9% |

Per family (corrected denominators; v4 = 79.3% of samples, v6 = 20.7%):

| | DB-IP v4 / v6 | GeoLite2 v4 / v6 |
|---|---|---|
| city | 100% / 100% | 48.7% / **24.9%** |

GeoLite2 is nearly useless on IPv6 — city coverage collapses to ~25% there,
while DB-IP covers v6 as thoroughly as v4. When GeoLite2 has no city it still
returns lat/lon: a silent fallback to the *country centroid* (e.g. a US range
resolving to the middle of Kansas).

## Agreement

- Country codes agree in **92.2%** of all 1M cases — and in **97.0%** when
  GeoLite2 actually has a city.
- Exact city-name match: **38.8%** when both have a city — but see
  "granularity" below; most "disagreements" are sub-city vs city naming, not
  wrong answers.
- Region agreement: **0.6%** — a pure *format* artifact, not real disagreement:
  GeoLite2 stores ISO codes (`SP`, `MN`, 2.1 chars mean), DB-IP full names
  (`São Paulo`, 9.2 chars mean), so the two never textually collide.
- Both DBs agree with the ip2asn *routing* country almost identically:
  DB-IP 84.1%, GeoLite2 85.0%. The residual ~15% in both cases is anycast/CDN
  space, where "physical country" and "routing country" legitimately diverge.

## Where the "164 km median gap" comes from

Raw haversine distance between the two DBs' coordinate answers over all ~1M
pairs: median **164 km**, p90 2,104 km — looks damning. Conditioned:

| condition | n | median | within 25 km | >2000 km |
|---|---|---|---|---|
| both DBs have a city | 437,816 | **10 km** | 62% | 5% |
| GeoLite2 cityless (country centroid) | 560,781 | **618 km** | 20% | 18% |

So wherever GeoLite2 *has* a city, it and DB-IP basically agree (median 10 km —
same neighborhood, different district). The scary aggregate distance is almost
entirely GeoLite2's country-centroid fallback. DB-IP's extra coverage isn't
just "more data" — it prevents silently-wrong coordinates.

## Granularity and terseness

- 21.1% of DB-IP city names carry parenthetical sub-city qualifiers
  (`Frankfurt am Main (Innenstadt I)`, `Singapore (Geylang)`); CTD's loader
  strips those for display.
- GeoLite2 is terser where it has data: ISO region codes vs full names, 8.6 vs
  12.1 chars mean city name. DB-IP's verbosity is handled by the existing
  display truncation.
- Most common "city disagreement" patterns are actually DB-IP being
  ward/street-level while GeoLite2 names the parent city:

```
'Shibuya City'              -> 'Tokyo'               2,316   (both correct)
'Frankfurt am Main (Innen…' -> 'Frankfurt am Main'   1,396
'London'                    -> 'City of London'      1,085
'Yongsan-dong'              -> 'Seoul'                 674
'Forest Lodge'              -> 'Sydney'                413
'Los Angeles (Central-A…'   -> 'Los Angeles'           392
```

- Genuine km-scale conflicts found (worth remembering as known-hard cases):

```
'Hanoi'                       -> 'Ho Chi Minh City'    1,358   (same cc VN, opposite ends)
'Jinrongjie (Xicheng District)' -> 'Shenzhen'           1,312   (Beijing vs Shenzhen!)
```

- Country disagreement tables are dominated by one pattern: GeoLite2 dropping
  to a centroid where it lacks data —

```
top DB-IP vs GeoLite2 cc disagreements:    top routing-cc -> DB-IP disagreements:
  GB -> US : 3,036                           US -> GB : 7,207
  JP -> US : 2,295                           NL -> US : 5,662
  DE -> US : 2,286                           US -> DE : 5,254
  US -> NL : 2,286                           US -> NL : 4,104
  CA -> US : 2,234                           US -> CA : 3,835
  ...
  US -> SC : 1,204   <- US ranges DB-IP places in Seychelles (offshore hosting)
```

## Verdict

**Update (2026-11-11): DB-IP is now the only supported city source — GeoLite2
loading, its downloader (`data/download_geoip.sh`) and attribution notice were
removed, and the loader API was renamed from `geolite2` to `ip2asn`. The
GeoLite2 figures below are kept as the historical justification.**

DB-IP City Lite is strictly the better fit for CTD as the primary city source:

1. 2.3× the city coverage (100% vs 44%), and full IPv6 coverage where GeoLite2
   manages only ~25%.
2. Wherever GeoLite2 is confident, the two agree to within ~10 km median — so
   switching costs nothing in accuracy.
3. Identical agreement with the routing country (~84-85%), and the TSV country
   keeps priority in CTD's display anyway.
4. Redistributable license, so it can be auto-fetched by `data/dbip-city.sh`
   like the other data files; GeoLite2 cannot be shipped at all.

GeoLite2-City remains supported as a fallback (loader picks whichever file is
newest); its only real edge is terser ISO region codes, which truncation
already compensates for.

**Caveat for daily use:** city-level output from *either* DB is an
ISP-registration guess, not ground truth — treat `[US/Minnesota/Minneapolis]`
as "routing context", and trust the ASN name beside it more.
