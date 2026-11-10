#!/usr/bin/env python3
"""
ip2asn_lookup.py - A GeoIP/ASN lookup module based on ip2asn-combined.tsv

This module replaces the deprecated maxminddb_geolite2 (geomind) module with
a lighter alternative that reads from the ip2asn-combined.tsv data file.

Usage:
    from ip2asn_lookup import geolite2
    reader = geolite2.reader()
    result = reader.get('1.1.1.1')
    print(result)
    # {'country': {'iso_code': 'US'}, 'asn': 13335, 'name': 'CLOUDFLARENET - Cloudflare, Inc.'}
    reader.close()

The API is compatible with maxminddb_geolite2's geolite2 module.
"""

import ipaddress
import radix
import os
import sys


class _GeoLite2Reader:
    """Reader for ip2asn-combined.tsv data using a radix tree for fast lookups."""

    def __init__(self, data_dir=None):
        """Initialize the reader by loading and indexing the TSV data.
        
        Args:
            data_dir: Directory containing ip2asn-combined.tsv.
                      Defaults to the 'data' subdirectory next to this file.
        """
        self._tree = radix.Radix()
        
        if data_dir is None:
            # Look for the TSV file in the same directory as this module
            script_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = script_dir
        
        tsv_path = os.path.join(data_dir, 'ip2asn-combined.tsv')
        
        if not os.path.exists(tsv_path):
            raise FileNotFoundError(f"Could not find {tsv_path}")
        
        self._load_data(tsv_path)
    
    def _load_data(self, tsv_path):
        """Load TSV data and build radix tree."""
        count = 0
        with open(tsv_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split('\t')
                if len(parts) < 5:
                    continue
                
                start_ip_str, end_ip_str, asn_str, country_code, asn_name = parts[0], parts[1], parts[2], parts[3], parts[4]
                
                try:
                    # Try to find a CIDR that encompasses this range
                    # We use a binary search approach to find the longest matching prefix
                    start_ip = ipaddress.ip_address(start_ip_str)
                    end_ip = ipaddress.ip_address(end_ip_str)
                    
                    # Calculate the network prefix
                    # We want the most specific prefix that covers the entire range
                    # For a /0 to /32 (IPv4) or /0 to /128 (IPv6) range
                    
                    if start_ip == end_ip:
                        # Single IP address
                        prefix_len = start_ip.max_prefixlen
                    else:
                        # Find common prefix bits
                        prefix_len = self._common_prefix_bits(start_ip, end_ip)
                    
                    # Use the network with that prefix length
                    if isinstance(start_ip, ipaddress.IPv4Address):
                        network = ipaddress.IPv4Network(f"{start_ip}/{prefix_len}", strict=False)
                    else:
                        network = ipaddress.IPv6Network(f"{start_ip}/{prefix_len}", strict=False)
                    
                    # Store data in radix tree
                    # ASN 0 means "not routed" or unknown
                    asn = int(asn_str) if asn_str.isdigit() else 0
                    country = country_code if country_code and country_code != 'None' else None
                    name = asn_name if asn_name and asn_name != 'Not routed' else None
                    
                    node = self._tree.add(str(network))
                    node.data['country_code'] = country
                    node.data['asn'] = asn
                    node.data['asn_name'] = name
                    
                    count += 1
                    
                except (ValueError, IndexError):
                    # Skip malformed entries
                    continue
        
        print(f"Loaded {count} IP ranges from {tsv_path}", file=sys.stderr)
    
    def _common_prefix_bits(self, start_ip, end_ip):
        """Calculate the number of common prefix bits between two IP addresses."""
        # Convert to integers
        start_int = int(start_ip)
        end_int = int(end_ip)
        
        # XOR to find differing bits
        xor = start_int ^ end_int
        
        if xor == 0:
            return start_ip.max_prefixlen
        
        # Count leading zeros (common prefix length)
        prefix_len = start_ip.max_prefixlen - xor.bit_length()
        return prefix_len
    
    def get(self, ip):
        """Look up IP address info.
        
        Args:
            ip: IP address string to look up
            
        Returns:
            Dictionary with country and ASN info, or None if not found.
            Format compatible with maxminddb_geolite2:
            {
                'country': {'iso_code': 'US'},
                'asn': 13335,
                'name': 'CLOUDFLARENET - Cloudflare, Inc.'
            }
        """
        try:
            ip_obj = ipaddress.ip_address(ip)
        except ValueError:
            return None
        
        # Search for covering node (most specific prefix that contains this IP)
        nodes = self._tree.search_covering(str(ip))
        
        if not nodes:
            return None
        
        # Get the most specific (longest prefix) match
        best_node = max(nodes, key=lambda n: n.prefixlen)
        
        result = {}
        
        if best_node.data.get('country_code'):
            result['country'] = {'iso_code': best_node.data['country_code']}
        
        if best_node.data.get('asn') and best_node.data['asn'] > 0:
            result['asn'] = best_node.data['asn']
        
        if best_node.data.get('asn_name'):
            result['name'] = best_node.data['asn_name']
        
        return result if result else None
    
    def close(self):
        """Close the reader and free resources."""
        self._tree = None


class geolite2:
    """Compatibility wrapper for maxminddb_geolite2 geolite2 module."""
    
    _reader = None
    
    @classmethod
    def reader(cls):
        """Get or create the reader instance."""
        if cls._reader is None:
            cls._reader = _GeoLite2Reader()
        return cls._reader
    
    @classmethod
    def close(cls):
        """Close the reader."""
        if cls._reader:
            cls._reader.close()
            cls._reader = None
