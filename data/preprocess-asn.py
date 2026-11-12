#!/usr/bin/env python3
"""
Preprocess ip2asn-combined.tsv into a compact JSON format.

This script:
1. Excludes ranges already tagged by any *-ctd-data.json source (default:
   ctd-data.json, the merged output of all provider/ASN scripts), so an
   IP is never labeled both by a tag name (e.g. FASTLY) and by the ip2asn
   ASN name at the same time. Exclusion is overlap-aware via a radix
   tree, not exact CIDR matching: ranges fully covered by a tag are
   dropped, ranges partially overlapping tags are split and only the
   uncovered parts are kept.
2. Groups adjacent IP ranges with the same ASN/country/owner
3. Truncates owner names to 6 characters
4. Outputs a compact JSON file for fast loading

Usage:
    python3 preprocess_asn.py [--input INPUT.TSV] [--output OUTPUT.json]

The output file is loaded instead of parsing the TSV on startup,
making startup ~10-50x faster.
"""

import argparse
import ipaddress
import json
import os
import sys
import time


def parse_args():
    parser = argparse.ArgumentParser(description='Preprocess ip2asn-combined.tsv to JSON')
    parser.add_argument('--input', default='ip2asn-combined.tsv',
                        help='Input TSV file path')
    parser.add_argument('--output', default='ip2asn-ctd-data.json',
                        help='Output JSON file path')
    parser.add_argument('--exclude', default='ctd-data.json',
                        help='JSON file with tagged ranges to exclude '
                             '(default: ctd-data.json, the merged output of '
                             'all provider/ASN scripts)')
    parser.add_argument('--compress', action='store_true',
                        help='Also create a .gz compressed version')
    return parser.parse_args()


def common_prefix_bits(start_ip, end_ip):
    """Calculate the number of common prefix bits between two IP addresses."""
    start_int = int(start_ip)
    end_int = int(end_ip)

    xor = start_int ^ end_ip

    if xor == 0:
        return start_ip.max_prefixlen

    prefix_len = start_ip.max_prefixlen - xor.bit_length()
    return prefix_len


def build_exclude_tree(exclude_json):
    """Build a radix tree of tagged CIDRs from a ctd-data JSON file.

    Accepts both merged files (ctd-data.json) and single-source files
    (91-asn-ctd-data.json): only the CIDR strings inside are relevant.
    """
    import radix
    import re

    if not exclude_json or not os.path.exists(exclude_json):
        return None

    print(f"Loading exclusions from {exclude_json} ...", file=sys.stderr)
    with open(exclude_json, 'r') as f:
        content = f.read()

    # Extract CIDR ranges, IPv4 ("23.235.32.0/20") and IPv6 ("2a04:4e40::/32")
    cidr_pattern = re.compile(r'"((?:\d+\.\d+\.\d+\.\d+|[0-9A-Fa-f:]+)/\d+)"')
    tree = radix.Radix()
    count = 0
    for cidr in set(cidr_pattern.findall(content)):
        try:
            tree.add(cidr)
            count += 1
        except ValueError:
            continue
    print(f"  Excluding {count:,} tagged ranges", file=sys.stderr)
    return tree


def subtract_tagged(start_ip, end_ip, network, tree):
    """Subtract tagged ranges from the [start_ip, end_ip] interval.

    Returns the remaining subranges as a list of networks. Only called
    when the radix tree says at least one tag overlaps the range.
    """
    tagged = []
    # Tags fully covering the range (probe both ends, either may be covered)
    for probe in (start_ip, end_ip):
        for node in tree.search_covering(str(probe)):
            tagged.append(ipaddress.ip_network(node.prefix, strict=False))
    # Tags fully inside the range
    for node in tree.search_covered(str(network)):
        tagged.append(ipaddress.ip_network(node.prefix, strict=False))

    # Deduplicate and keep only tags intersecting [start, end]
    s = int(start_ip)
    e = int(end_ip)
    intervals = sorted(set(
        (max(int(n.network_address), s), min(int(n.broadcast_address), e))
        for n in tagged
    ))
    intervals = [(a, b) for a, b in intervals if a <= b]

    # Walk the interval, cutting out each tagged piece
    pieces = []
    cur = s
    for a, b in intervals:
        if a > cur:
            pieces.append((cur, a - 1))
        cur = max(cur, b + 1)
        if cur > e:
            break
    if cur <= e:
        pieces.append((cur, e))

    networks = []
    for a, b in pieces:
        networks.extend(ipaddress.summarize_address_range(
            ipaddress.ip_address(a), ipaddress.ip_address(b)))
    return networks


def preprocess_tsv(input_path, output_path, compress=False, exclude_json='ctd-data.json'):
    """Preprocess the TSV file into a compact JSON format."""

    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found", file=sys.stderr)
        sys.exit(1)

    print(f"Reading {input_path} ...", file=sys.stderr)
    start_time = time.time()

    # Load tagged ranges to exclude (overlap-aware, via radix tree)
    excluded_tree = build_exclude_tree(exclude_json)

    # Count total lines for progress
    total_lines = sum(1 for _ in open(input_path, 'r'))
    print(f"  Total lines: {total_lines:,}", file=sys.stderr)

    # Data structure: {asn: {'country': ..., 'name': ..., 'ranges': [...]}}
    asn_data = {}
    lines_processed = 0
    ranges_dropped = 0
    ranges_split = 0

    with open(input_path, 'r') as f:
        for line in f:
            lines_processed += 1

            # Show progress every 100k lines
            if lines_processed % 100000 == 0:
                pct = lines_processed / total_lines * 100
                print(f"\r  Processed {lines_processed:,}/{total_lines:,} ({pct:.0f}%)",
                      end='', file=sys.stderr)

            line = line.strip()
            if not line:
                continue

            parts = line.split('\t')
            if len(parts) < 5:
                continue

            start_ip_str, end_ip_str, asn_str, country_code, asn_name = \
                parts[0], parts[1], parts[2], parts[3], parts[4]

            try:
                start_ip = ipaddress.ip_address(start_ip_str)
                end_ip = ipaddress.ip_address(end_ip_str)

                # Calculate network prefix
                xor = int(start_ip) ^ int(end_ip)
                if xor == 0:
                    prefix_len = start_ip.max_prefixlen
                else:
                    prefix_len = start_ip.max_prefixlen - xor.bit_length()

                if isinstance(start_ip, ipaddress.IPv4Address):
                    network = ipaddress.IPv4Network(f"{start_ip}/{prefix_len}", strict=False)
                else:
                    network = ipaddress.IPv6Network(f"{start_ip}/{prefix_len}", strict=False)

                # Exclude ranges already tagged in the exclude JSON:
                # - fully covered by a tag -> drop the whole range
                # - partially overlapping tag(s) -> split, keep the rest
                networks_to_add = [str(network)]
                if excluded_tree is not None:
                    if excluded_tree.search_covering(str(network)):
                        networks_to_add = []
                        ranges_dropped += 1
                    elif excluded_tree.search_covered(str(network)):
                        networks_to_add = [str(n) for n in
                                           subtract_tagged(start_ip, end_ip, network,
                                                           excluded_tree)]
                        if not networks_to_add:
                            ranges_dropped += 1
                        else:
                            ranges_split += 1

                asn = int(asn_str) if asn_str.isdigit() else 0
                country = country_code if country_code and country_code != 'None' else None
                name = asn_name if asn_name and asn_name != 'Not routed' else None

                if name:
                    # Truncate name to 6 characters
                    name = name[:6]

                # Store in data structure
                if asn not in asn_data:
                    asn_data[asn] = {
                        'country': country,
                        'name': name,
                        'ranges': []
                    }

                # Store as CIDR strings for JSON
                asn_data[asn]['ranges'].extend(networks_to_add)

            except (ValueError, IndexError):
                continue

    print(f"\r  Processed {lines_processed:,}/{total_lines:,} (100%)",
          end='\n', file=sys.stderr)
    print(f"  Ranges dropped (tag-covered): {ranges_dropped:,}, "
          f"split around tags: {ranges_split:,}", file=sys.stderr)

    # Group ranges by (country, name) for same ASN
    # This creates a more compact structure
    print("Grouping ranges by (country, name) ...", file=sys.stderr)
    grouped_data = {}

    for asn, data in asn_data.items():
        country = data['country'] or ''
        name = data['name'] or ''
        # Use a string key for JSON compatibility
        key = f"{country}|{name}"

        if key not in grouped_data:
            grouped_data[key] = {
                'asn': asn,
                'country': country if country else None,
                'name': name if name else None,
                'ranges': []
            }

        grouped_data[key]['ranges'].extend(data['ranges'])

    # Sort ranges by IP address for efficient lookup
    # Sort IPv4 and IPv6 separately since they can't be compared
    print("Sorting ranges ...", file=sys.stderr)
    for key, data in grouped_data.items():
        ipv4_ranges = []
        ipv6_ranges = []

        for r in data['ranges']:
            try:
                net = ipaddress.ip_network(r, strict=False)
                if isinstance(net.network_address, ipaddress.IPv4Address):
                    ipv4_ranges.append(r)
                else:
                    ipv6_ranges.append(r)
            except ValueError:
                ipv4_ranges.append(r)  # Keep in IPv4 list if unknown

        # Sort each group separately
        ipv4_ranges.sort(key=lambda r: ipaddress.ip_network(r, strict=False).network_address)
        ipv6_ranges.sort(key=lambda r: ipaddress.ip_network(r, strict=False).network_address)

        # Combine: IPv4 first, then IPv6
        data['ranges'] = ipv4_ranges + ipv6_ranges

    # Create output structure
    output = {
        'version': 1,
        'source': 'ip2asn-combined.tsv',
        'total_entries': len(grouped_data),
        'data': grouped_data
    }

    # Write JSON file
    print(f"Writing {output_path} ...", file=sys.stderr)
    with open(output_path, 'w') as f:
        json.dump(output, f, separators=(',', ':'))

    file_size = os.path.getsize(output_path)
    print(f"  Output size: {file_size:,} bytes ({file_size/1024:.1f} KB)", file=sys.stderr)

    if compress:
        print("Compressing ...", file=sys.stderr)
        import gzip
        with open(output_path, 'rb') as f_in:
            with gzip.open(output_path + '.gz', 'wb') as f_out:
                f_out.writelines(f_in)
        gz_size = os.path.getsize(output_path + '.gz')
        print(f"  Compressed size: {gz_size:,} bytes ({gz_size/1024:.1f} KB)", file=sys.stderr)

    elapsed = time.time() - start_time
    print(f"Done in {elapsed:.1f}s", file=sys.stderr)


if __name__ == '__main__':
    args = parse_args()
    preprocess_tsv(args.input, args.output, args.compress, args.exclude)
