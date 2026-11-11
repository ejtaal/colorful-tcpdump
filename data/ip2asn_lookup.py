#!/usr/bin/env python3
"""
ip2asn_lookup.py - A GeoIP/ASN lookup module based on ip2asn-combined.tsv + DB-IP City Lite

This module replaces the deprecated maxminddb_geolite2 (geomind) module with
a combination of:
- ip2asn-combined.tsv for ASN and country data
- DB-IP's City Lite mmdb (free, CC BY 4.0, download with data/dbip-city.sh)
  for city/subdivision data

Usage:
    from ip2asn_lookup import ip2asn
    reader = ip2asn.reader()
    result = reader.get('1.1.1.1')
    print(result)
    reader.close()
"""

import ipaddress
import glob
import gzip
import radix
import maxminddb
import os
import re
import sys


class _IP2ASNReader:
    """Reader for ip2asn-combined.tsv + DB-IP City Lite data using radix trees for fast lookups."""

    def __init__(self, data_dir=None):
        """Initialize the reader by loading and indexing the data files.
        
        Args:
            data_dir: Directory containing the data files.
                      Defaults to the 'data' subdirectory next to this file.
        """
        self._asn_tree = radix.Radix()
        self._city_reader = None
        
        if data_dir is None:
            # Look for the data files in the same directory as this module
            script_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = script_dir
        
        self._data_dir = data_dir
        
        # Load ASN/country data from TSV
        tsv_path = os.path.join(data_dir, 'ip2asn-combined.tsv')
        if os.path.exists(tsv_path):
            self._load_asn_data(tsv_path)
        else:
            print(f"Warning: Could not find {tsv_path}", file=sys.stderr)
        
        # Load city data from mmdb (optional)
        self._city_reader = self._open_city_mmdb(data_dir)

    def _open_city_mmdb(self, data_dir):
        """Open the newest DB-IP City Lite mmdb found next to the other data files.

        Supported files (newest mtime wins):
            dbip-city-lite-<date>.mmdb / .mmdb.gz  (data/dbip-city.sh)
        A bundled .mmdb.gz is decompressed once, to .mmdb, on first use.
        """
        mmdb_files = glob.glob(os.path.join(data_dir, 'dbip-city-lite-*.mmdb*'))
        if not mmdb_files:
            print("No city mmdb found (city lookups disabled; run data/dbip-city.sh to get one)",
                  file=sys.stderr)
            return None

        chosen = max(mmdb_files, key=os.path.getmtime)

        if chosen.endswith('.gz'):
            unpacked = chosen[:-3]
            if unpacked in mmdb_files:
                # Both the .gz and its unpacked copy are present (e.g. after a
                # re-download): just use the unpacked copy.
                chosen = unpacked
            else:
                print(f"Decompressing {chosen} -> {unpacked} ...", file=sys.stderr)
                with gzip.open(chosen, 'rb') as src, open(unpacked, 'wb') as dst:
                    while True:
                        chunk = src.read(1 << 20)
                        if not chunk:
                            break
                        dst.write(chunk)
                chosen = unpacked

        try:
            reader = maxminddb.open_database(chosen)
            print(f"Loaded city data from {chosen}", file=sys.stderr)
            return reader
        except Exception as e:
            print(f"Warning: Could not load city database {chosen}: {e}", file=sys.stderr)
            return None
    
    def _load_asn_data(self, tsv_path):
        """Load ASN/country data from TSV and build radix tree."""
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
                    start_ip = ipaddress.ip_address(start_ip_str)
                    end_ip = ipaddress.ip_address(end_ip_str)
                    
                    if start_ip == end_ip:
                        prefix_len = start_ip.max_prefixlen
                    else:
                        prefix_len = self._common_prefix_bits(start_ip, end_ip)
                    
                    if isinstance(start_ip, ipaddress.IPv4Address):
                        network = ipaddress.IPv4Network(f"{start_ip}/{prefix_len}", strict=False)
                    else:
                        network = ipaddress.IPv6Network(f"{start_ip}/{prefix_len}", strict=False)
                    
                    asn = int(asn_str) if asn_str.isdigit() else 0
                    country = country_code if country_code and country_code != 'None' else None
                    name = asn_name if asn_name and asn_name != 'Not routed' else None
                    
                    node = self._asn_tree.add(str(network))
                    node.data['country_code'] = country
                    node.data['asn'] = asn
                    node.data['asn_name'] = name
                    
                    count += 1
                    
                except (ValueError, IndexError):
                    continue
        
        print(f"Loaded {count} ASN ranges from {tsv_path}", file=sys.stderr)
    
    def _common_prefix_bits(self, start_ip, end_ip):
        """Calculate the number of common prefix bits between two IP addresses."""
        start_int = int(start_ip)
        end_int = int(end_ip)
        
        xor = start_int ^ end_int
        
        if xor == 0:
            return start_ip.max_prefixlen
        
        prefix_len = start_ip.max_prefixlen - xor.bit_length()
        return prefix_len
    
    def _get_city_info(self, ip):
        """Get city/subdivision info from the DB-IP City Lite database."""
        if not self._city_reader:
            return None
        
        try:
            result = self._city_reader.get(str(ip))
            if not result:
                return None
            
            city_info = {}
            
            # Get country (only used for ranges the ASN table is missing)
            country = result.get('country')
            if country and country.get('iso_code'):
                city_info['country'] = country['iso_code']
            
            # Get city name
            city = result.get('city')
            if city and city.get('names'):
                # Drop parenthetical qualifiers such as 'Amsterdam (Amsterdam City
                # Centre)': they tend to make truncated display strings ugly.
                city_info['city'] = re.sub(r'\s*\([^)]*\)\s*', '', city['names'].get('en', '')).strip()
            
            # Get subdivision (state/region)
            subdivisions = result.get('subdivisions', [])
            if subdivisions and subdivisions[0].get('names'):
                city_info['subdivision'] = subdivisions[0]['names'].get('en', '')
            
            return city_info if city_info else None
        except Exception:
            return None
    
    def get(self, ip):
        """Look up IP address info.
        
        Args:
            ip: IP address string to look up
            
        Returns:
            Dictionary with country, city, subdivision, and ASN info:
            {
                'country': {'iso_code': 'US'},
                'subdivisions': [{'iso_code': 'CA'}],
                'asn': 13335,
                'name': 'CLOUDFLARENET - Cloudflare, Inc.',
                'city': 'Los Angeles',
                'subdivision': 'California'
            }
        """
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            return None
        
        result = {}
        
        # Get ASN/country data from radix tree
        nodes = self._asn_tree.search_covering(str(ip))
        if nodes:
            best_node = max(nodes, key=lambda n: n.prefixlen)
            
            if best_node.data.get('country_code'):
                result['country'] = {'iso_code': best_node.data['country_code']}
            
            if best_node.data.get('asn') and best_node.data['asn'] > 0:
                result['asn'] = best_node.data['asn']
            
            if best_node.data.get('asn_name'):
                result['name'] = best_node.data['asn_name']
        
        # Get city data from mmdb
        city_info = self._get_city_info(ip)
        if city_info:
            # Fill in country from the city database only when the ASN table
            # is missing (or routing-blind for) this range.
            if 'country' not in result and city_info.get('country'):
                result['country'] = {'iso_code': city_info['country']}
            if city_info.get('city'):
                result['city'] = {'names': {'en': city_info['city']}}
            if city_info.get('subdivision'):
                result['subdivision'] = city_info['subdivision']
                result.setdefault('subdivisions', [
                    {'iso_code': '', 'names': {'en': city_info['subdivision']}}
                ])
        
        return result if result else None
    
    def close(self):
        """Close the reader and free resources."""
        self._asn_tree = None
        if self._city_reader:
            self._city_reader.close()
            self._city_reader = None


class geolite2:
    """Compatibility wrapper for maxminddb_geolite2 geolite2 module."""
    
    _reader = None
    
    @classmethod
    def reader(cls):
        """Get or create the reader instance."""
        if cls._reader is None:
            cls._reader = _IP2ASNReader()
        return cls._reader
    
    @classmethod
    def close(cls):
        """Close the reader."""
        if cls._reader:
            cls._reader.close()
            cls._reader = None
