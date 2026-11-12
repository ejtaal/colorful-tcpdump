#!/usr/bin/env python3
"""
Parse DB-IP City Lite mmdb into a compact binary file for redistribution.

DB-IP's City Lite database is licensed CC BY 4.0, so a parsed/modified
version may be redistributed as long as attribution is kept and the fact
that it is modified is noted (done via the 'source' header field and the
README).

Why binary and not JSON: the database contains ~13M distinct IP ranges.
A JSON with CIDR strings is ~260 MB and building a radix tree from it
takes ~40 s and ~8 GB RAM, while the same ranges as sorted (start, end,
group) arrays load in a few seconds, take ~300 MB of RAM, and are looked
up with stdlib bisect (see data/ip2asn_lookup.py). The result gzips to
about the same size as the original mmdb anyway.

Output: dbip-city-ctd-data.bin.gz, loaded by data/ip2asn_lookup.py when
no mmdb is found, which silences the "No city data found" warning.

File format (all integers little-endian, all v6 keys 16 bytes
big-endian, i.e. ipaddress.IPv6Address.packed):

    line 1: JSON header, terminated by \\n:
            {"version": 1, "source": "...", "source_mmdb": "...",
             "groups": ["CC|Subdivision|City", ...],
             "n4": <v4 range count>, "n6": <v6 range count>}
    then:   n4 * u32  v4 range start (ipaddress int)
            n4 * u32  v4 range end (inclusive)
            n4 * u32  group index
            n6 * 16B  v6 range start (packed, sorted)
            n6 * 16B  v6 range end (packed, inclusive)
            n6 * u32  group index

Usage (from anywhere):
    ./data/dbip-city.sh                  # fetch the mmdb first, if needed
    python3 data/dbip-city-parse.py
"""

import argparse
import gzip
import ipaddress
import json
import os
import re
import struct
import sys
import time

import maxminddb

HERE = os.path.dirname(os.path.abspath(__file__))


def parse_args():
    parser = argparse.ArgumentParser(
        description='Parse DB-IP City Lite mmdb into compact binary')
    parser.add_argument('--input', default=None,
                        help='Input mmdb file (default: newest '
                             'dbip-city-lite-*.mmdb[.gz] next to this script)')
    parser.add_argument('--output', default=os.path.join(
                            HERE, 'dbip-city-ctd-data.bin.gz'),
                        help='Output file path')
    return parser.parse_args()


def find_newest_mmdb(directory):
    """Find the newest dbip-city-lite-*.mmdb[.gz] in directory."""
    import glob
    candidates = (glob.glob(os.path.join(directory, 'dbip-city-lite-*.mmdb')) +
                  glob.glob(os.path.join(directory, 'dbip-city-lite-*.mmdb.gz')))
    if not candidates:
        return None
    return max(candidates, key=os.path.getmtime)


def merge_ranges(ranges):
    """Merge a list of (start_int, end_int) into disjoint intervals.

    Adjacent intervals (b + 1 == next a) are merged too.
    """
    ranges = sorted(ranges)
    merged = []
    for a, b in ranges:
        if merged and a <= merged[-1][1] + 1:
            if b > merged[-1][1]:
                merged[-1][1] = b
        else:
            merged.append([a, b])
    return merged


def parse_mmdb(input_path, output_path):
    print(f"Reading {input_path} ...", file=sys.stderr)
    start_time = time.time()

    if input_path.endswith('.gz'):
        # maxminddb.open_database needs a real file, not bytes or a
        # gzip stream: decompress to a temp file first.
        import tempfile
        tmp = tempfile.NamedTemporaryFile(suffix='.mmdb', delete=False)
        try:
            print(f"Decompressing {input_path} -> {tmp.name} ...",
                  file=sys.stderr)
            with gzip.open(input_path, 'rb') as src, open(tmp.name, 'wb') as dst:
                while True:
                    chunk = src.read(1 << 20)
                    if not chunk:
                        break
                    dst.write(chunk)
            reader = maxminddb.open_database(tmp.name)
        finally:
            os.unlink(tmp.name)
    else:
        reader = maxminddb.open_database(input_path)

    # Group ranges by (country, subdivision, city). Same parenthetical
    # qualifier stripping as ip2asn_lookup.py's mmdb lookups.
    qualifier_re = re.compile(r'\s*\([^)]*\)\s*')
    groups = {}  # (cc, subdivision, city) -> [(start_int, end_int), ...]
    count = 0
    for network, record in reader:
        count += 1
        if count % 1000000 == 0:
            print(f"\r  {count:,} networks ...", end='', file=sys.stderr)

        if not record:
            continue
        country = record.get('country') or {}
        cc = country.get('iso_code') or ''
        city = (record.get('city') or {}).get('names', {}).get('en', '')
        if city:
            city = qualifier_re.sub('', city).strip()
        subdivisions = record.get('subdivisions') or []
        subdivision = ''
        if subdivisions:
            subdivision = (subdivisions[0].get('names') or {}).get('en', '')

        if not (cc or city or subdivision):
            continue

        key = (cc, subdivision, city)
        start = int(network.network_address)
        end = int(network.broadcast_address)
        groups.setdefault(key, []).append((start, end))
    reader.close()

    print(f"\r  {count:,} networks, {len(groups):,} (cc, subdivision, city) "
          f"groups", end='\n', file=sys.stderr)

    print("Merging ranges per group ...", file=sys.stderr)
    group_names = []
    v4 = []  # (start, end, group_idx)
    v6 = []
    total_ranges = 0
    for key, ranges in groups.items():
        idx = len(group_names)
        group_names.append('|'.join(key))
        for a, b in merge_ranges(ranges):
            total_ranges += 1
            if a < (1 << 32):
                v4.append((a, b, idx))
            else:
                v6.append((a, b, idx))
    del groups

    v4.sort()
    v6.sort()
    n4, n6 = len(v4), len(v6)
    print(f"  {total_ranges:,} ranges (v4 {n4:,}, v6 {n6:,})",
          file=sys.stderr)

    # Attribution required by CC BY 4.0; 'modified' because this is a
    # parsed, grouped subset rather than the original database.
    header = json.dumps({
        'version': 1,
        'source': 'DB-IP City Lite (https://db-ip.com), CC BY 4.0, modified',
        'source_mmdb': os.path.basename(input_path),
        'groups': group_names,
        'n4': n4,
        'n6': n6,
    }).encode('utf-8') + b'\n'

    print(f"Writing {output_path} ...", file=sys.stderr)
    with gzip.open(output_path, 'wb', compresslevel=9) as f:
        f.write(header)
        # v4: starts, ends, group indices as u32
        f.write(struct.pack(f'<{n4}I', *(r[0] for r in v4)))
        f.write(struct.pack(f'<{n4}I', *(r[1] for r in v4)))
        f.write(struct.pack(f'<{n4}I', *(r[2] for r in v4)))
        # v6: starts and ends as 16-byte big-endian packed addresses
        f.write(b''.join(
            (r[0]).to_bytes(16, 'big') for r in v6))
        f.write(b''.join(
            (r[1]).to_bytes(16, 'big') for r in v6))
        f.write(struct.pack(f'<{n6}I', *(r[2] for r in v6)))

    file_size = os.path.getsize(output_path)
    print(f"  Output size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)",
          file=sys.stderr)

    elapsed = time.time() - start_time
    print(f"Done in {elapsed:.1f}s", file=sys.stderr)


if __name__ == '__main__':
    args = parse_args()

    input_path = args.input
    if input_path is None:
        input_path = find_newest_mmdb(HERE)
        if input_path is None:
            print("No dbip-city-lite-*.mmdb[.gz] found. Run data/dbip-city.sh "
                  "first, or pass --input.", file=sys.stderr)
            sys.exit(1)

    parse_mmdb(input_path, args.output)
