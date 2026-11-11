#!/usr/bin/env python3
"""Compare DB-IP City Lite vs GeoLite2-City over 1,000,000 randomly sampled
routed IPs (uniform over routed ranges from ip2asn-combined.tsv)."""

import ipaddress
import math
import random
import time
from collections import Counter

import maxminddb

N = 1_000_000
random.seed(1234)
t0 = time.time()

# --- load routed ranges from the TSV (ASN known + country known) ---
starts, ends, ccs = [], [], []
with open('data/ip2asn-combined.tsv') as f:
    for line in f:
        p = line.rstrip('\n').split('\t')
        if len(p) == 5 and p[2].isdigit() and int(p[2]) > 0 and p[3] not in ('', 'None'):
            starts.append(int(ipaddress.ip_address(p[0])))
            ends.append(int(ipaddress.ip_address(p[1])))
            ccs.append(p[3][:2])
n_ranges = len(starts)
print(f"loaded {n_ranges} routed ranges in {time.time()-t0:.1f}s", flush=True)

dbip = maxminddb.open_database('data/dbip-city-lite-2026-11.mmdb')
try:
    geo2 = maxminddb.open_database('data/GeoLite2-City.mmdb')
except Exception:
    # GeoLite2 support was removed from the repo; this historical comparison
    # script needs the file present to reproduce the two-way comparison.
    raise SystemExit("data/GeoLite2-City.mmdb not found - "
                     "this historical comparison script requires both files")

def haversine(a, b):
    """distance in km between two (lat, lon) tuples"""
    lat1, lon1, lat2, lon2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(min(1.0, h)))

def rec(db, s):
    r = db.get(s)
    if not r:
        return None, None, None, None, None
    country = (r.get('country') or {}).get('iso_code')
    subs = r.get('subdivisions') or [{}]
    region = subs[0].get('iso_code') or subs[0].get('names', {}).get('en')
    city = (r.get('city') or {}).get('names', {}).get('en')
    loc = r.get('location') or {}
    ll = (loc['latitude'], loc['longitude']) if 'latitude' in loc else None
    return country, region, city, ll, r.get('registered_country', {}).get('iso_code')

# stats
keys = ('cc', 'reg', 'city', 'll')
stats = {f'{db}_{k}_{fam}': 0 for db in ('db', 'g2') for k in keys for fam in ('v4', 'v6')}
stats.update({k: 0 for k in (
    'cc_match', 'city_match', 'reg_match',
    'cc_db_vs_tsv', 'cc_g2_vs_tsv',
    'cc_db_vs_tsv_v4', 'cc_db_vs_tsv_v6',
    'both_city', 'cc_match_both_city',
    'db_qualifier', 'dist_n',
    'regcode_g2',  # g2 region is a short ISO-like code
)})
cc_disagree = Counter()          # (dbip cc, geolite cc) -> count
cc_disagree_routing = Counter()  # (tsv cc, dbip cc) -> count
city_disagree_pairs = Counter()  # (dbip city, g2 city) -> count
reglen_db, reglen_g2, citylen_db, citylen_g2 = 0, 0, 0, 0
distances = []

for i in range(N):
    ri = random.randrange(n_ranges)
    x = random.randint(starts[ri], ends[ri])
    fam = 'v4' if x < 2**32 else 'v6'
    s = str(ipaddress.ip_address(x))
    tcc = ccs[ri]

    dcc, dreg, dcity, dll, _ = rec(dbip, s)
    gcc, greg, gcity, gll, _ = rec(geo2, s)

    st = stats
    st['db_cc_' + fam] += dcc is not None
    st['db_reg_' + fam] += dreg is not None
    st['db_city_' + fam] += dcity is not None
    st['db_ll_' + fam] += dll is not None
    st['g2_cc_' + fam] += gcc is not None
    st['g2_reg_' + fam] += greg is not None
    st['g2_city_' + fam] += gcity is not None
    st['g2_ll_' + fam] += gll is not None

    if dcc is not None:
        reglen_db += len(dreg) if dreg else 0
        citylen_db += len(dcity) if dcity else 0
        if dcity and '(' in dcity:
            st['db_qualifier'] += 1
        if dcc == tcc:
            st['cc_db_vs_tsv'] += 1
            st['cc_db_vs_tsv_' + fam] += 1
        else:
            cc_disagree_routing[(tcc, dcc)] += 1
    if gcc is not None:
        reglen_g2 += len(greg) if greg else 0
        citylen_g2 += len(gcity) if gcity else 0
        if greg is not None and len(greg) <= 3:
            st['regcode_g2'] += 1
        if gcc == tcc:
            st['cc_g2_vs_tsv'] += 1

    if dcc is not None and gcc is not None:
        if dcc == gcc:
            st['cc_match'] += 1
        else:
            cc_disagree[(dcc, gcc)] += 1
    if dcity is not None and gcity is not None:
        st['both_city'] += 1
        if dcity == gcity:
            st['city_match'] += 1
            if dreg == greg:
                st['reg_match'] += 1
        else:
            if len(city_disagree_pairs) < 500_000:
                city_disagree_pairs[(dcity, gcity)] += 1
    if dll is not None and gll is not None:
        if len(distances) < 1_000_000:
            distances.append(haversine(dll, gll))
        st['dist_n'] += 1

    if (i + 1) % 100_000 == 0:
        print(f"  {i+1:>9,}/{N:,}  ({time.time()-t0:.0f}s)", flush=True)

# --- report ---
print('\n=== 1,000,000 random routed IPs (uniform over ip2asn ranges) ===\n')
def pct(a, fam=None):
    denom = N // 2 if fam else N
    return f"{100*a/denom:.1f}%"

print(f"{'metric':<32}{'DB-IP':>9}{'GeoLite2':>10}")
for k, label in [('cc', 'has country'), ('reg', 'has region/state'),
                 ('city', 'has city'), ('ll', 'has lat/lon')]:
    db_sum = stats['db_' + k + '_v4'] + stats['db_' + k + '_v6']
    g2_sum = stats['g2_' + k + '_v4'] + stats['g2_' + k + '_v6']
    print(f"{label:<32}{pct(db_sum):>9}{pct(g2_sum):>10}")

print('\nper family:')
print(f"{'metric':<32}{'DB-IP v4':>9}{'DB-IP v6':>9}{'GeoLite v4':>12}{'GeoLite v6':>12}")
for k, label in [('cc', 'has country'), ('reg', 'has region/state'), ('city', 'has city')]:
    print(f"{label:<32}{pct(stats['db_'+k+'_v4'], 1):>9}{pct(stats['db_'+k+'_v6'], 1):>9}"
          f"{pct(stats['g2_'+k+'_v4'], 1):>12}{pct(stats['g2_'+k+'_v6'], 1):>12}")

print(f"\ncountry agreement (both present)          : {stats['cc_match']:,}/{N:,} "
      f"= {100*stats['cc_match']/N:.1f}%")
print(f"city agreement (both city present)        : {stats['city_match']:,}/{stats['both_city']:,} "
      f"= {100*stats['city_match']/max(1,stats['both_city']):.1f}%")
print(f"region agreement (both city present)      : {stats['reg_match']:,}/{stats['both_city']:,} "
      f"= {100*stats['reg_match']/max(1,stats['both_city']):.1f}%")
print(f"DB-IP cc agrees with ip2asn routing cc    : {pct(stats['cc_db_vs_tsv'])}  "
      f"(v4 {pct(stats['cc_db_vs_tsv_v4'],1)}, v6 {pct(stats['cc_db_vs_tsv_v6'],1)})")
print(f"GeoLite2 cc agrees with ip2asn routing cc : {pct(stats['cc_g2_vs_tsv'])}")

print('\nterseness (mean string length when present):')
print(f"  region   DB-IP {reglen_db/max(1,stats['db_reg_v4']+stats['db_reg_v6']):.1f} chars"
      f"   GeoLite2 {reglen_g2/max(1,stats['g2_reg_v4']+stats['g2_reg_v6']):.1f} chars"
      f"   (GeoLite2 uses <=3 char ISO codes {pct(stats['regcode_g2'])} of the time)")
print(f"  city     DB-IP {citylen_db/max(1,stats['db_city_v4']+stats['db_city_v6']):.1f} chars"
      f"   GeoLite2 {citylen_g2/max(1,stats['g2_city_v4']+stats['g2_city_v6']):.1f} chars"
      f"   (DB-IP parenthetical qualifiers: {pct(stats['db_qualifier'])})")

if distances:
    distances.sort()
    d = lambda q: distances[int(len(distances)*q)]
    print(f"\nlat/lon distance between DB-IP and GeoLite2 answers ({stats['dist_n']:,} pairs):")
    print(f"  median {d(0.5):.0f} km   p75 {d(0.75):.0f} km   p90 {d(0.9):.0f} km   p99 {d(0.99):.0f} km")
    within = lambda km: 100*sum(1 for x in distances if x <= km)/len(distances)
    print(f"  within 25 km {within(25):.0f}%   within 100 km {within(100):.0f}%   "
          f"within 500 km {within(500):.0f}%   >2000 km {100-within(2000):.0f}%")

print('\ntop DB-IP vs GeoLite2 country disagreements (dbip -> geolite : count):')
for (a, b), c in cc_disagree.most_common(10):
    print(f"  {a} -> {b} : {c:,}")

print('\ntop routing-cc -> DB-IP disagreements (routing -> dbip : count):')
for (a, b), c in cc_disagree_routing.most_common(10):
    print(f"  {a} -> {b} : {c:,}")

print('\nmost common city-name disagreements where DB-IP says X and GeoLite2 says Y:')
for (a, b), c in city_disagree_pairs.most_common(12):
    print(f"  {a!r} -> {b!r} : {c:,}")

print(f"\ntotal runtime {time.time()-t0:.0f}s")
