#!/usr/bin/env python3
"""
Preprocess ip2asn-combined.tsv into a compact JSON format.

This script:
1. Groups adjacent IP ranges with the same ASN/country/owner
2. Truncates owner names to 6 characters
3. Outputs a compact JSON file for fast loading

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
    parser.add_argument('--exclude', default=None,
                        help='JSON file with ranges to exclude (e.g., 91-asn-ctd-data.json)')
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


def preprocess_tsv(input_path, output_path, compress=False, exclude_json=None):
    """Preprocess the TSV file into a compact JSON format."""
    
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found", file=sys.stderr)
        sys.exit(1)
    
    print(f"Reading {input_path} ...", file=sys.stderr)
    start_time = time.time()
    
    # Load excluded ranges from existing ASN JSON if provided
    excluded_ranges = set()
    if exclude_json and os.path.exists(exclude_json):
        print(f"Loading exclusions from {exclude_json} ...", file=sys.stderr)
        with open(exclude_json, 'r') as f:
            content = f.read()
        # Use regex to extract CIDR ranges (e.g., "23.160.32.0/24")
        import re
        cidr_pattern = re.compile(r'"(\d+\.\d+\.\d+\.\d+/\d+)"')
        excluded_ranges = set(cidr_pattern.findall(content))
        print(f"  Excluding {len(excluded_ranges):,} ranges", file=sys.stderr)
    
    # Count total lines for progress
    total_lines = sum(1 for _ in open(input_path, 'r'))
    print(f"  Total lines: {total_lines:,}", file=sys.stderr)
    
    # Data structure: {asn: {'country': ..., 'name': ..., 'ranges': [...]}}
    asn_data = {}
    lines_processed = 0
    
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
                
                # Skip if this range is already in the exclusion list
                if str(network) in excluded_ranges:
                    continue
                
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
                
                # Store as CIDR string for JSON
                asn_data[asn]['ranges'].append(str(network))
                
            except (ValueError, IndexError):
                continue
    
    print(f"\r  Processed {lines_processed:,}/{total_lines:,} (100%)", 
          end='\n', file=sys.stderr)
    
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
