#!/usr/bin/env python3

#8from netifaces import interfaces, ifaddresses, AF_INET
from netifaces import *

all_adds = []
all_broadcasts = []

all_ifs = []

for ifaceName in interfaces():
    #all_ifs.append( ifaddresses(ifaceName))
    for key, value in ifaddresses(ifaceName).items():
        #print(key, '->', value)
        all_ifs.append( value)
        if 'addr' in value[0]:
            #print( 'addr', value[0]['addr'])
            if value[0]['addr'] not in all_adds:
                all_adds.append( value[0]['addr'])
        if 'broadcast' in value[0]:
            #print( 'broadcast', value[0]['broadcast'])
            if value[0]['broadcast'] not in all_broadcasts:
                all_broadcasts.append( value[0]['broadcast'])

"""
   _____      _             __       _           
  / ____|    | |           / _|     | |          
 | |     ___ | | ___  _ __| |_ _   _| |          
 | |    / _ \| |/ _ \| '__|  _| | | | |          
 | |___| (_) | | (_) | |  | | | |_| | |          
  \_____\___/|_|\___/|_| _|_|  \__,_|_|          
 |__   __/ ____|  __ \  | |                      
    | | | |    | |__) |_| |_   _ _ __ ___  _ __  
    | | | |    |  ___/ _` | | | | '_ ` _ \| '_ \ 
    | | | |____| |  | (_| | |_| | | | | | | |_) |
    |_|  \_____|_|   \__,_|\__,_|_| |_| |_| .__/ 
                                          | |    
                                          |_|    
"""

    #addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
    #print ( ifaceName, 'addr', [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_LINK, [{'addr':'No IP addr'}] )])

    #if ( 'broadcast' in i):
    #print ( ifaceName, 'broadcast', ifaddresses(ifaceName) )
    #print( '%s: %s' % (ifaceName, ', '.join(addresses)) )


from colorama import *
init()
"""
Available formatting constants are:
Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
Style: DIM, NORMAL, BRIGHT, RESET_ALL
"""
nice_colors = [
Back.BLUE + Fore.GREEN,
Back.BLUE + Fore.YELLOW,
#Back.BLUE + Fore.MAGENTA,
Back.BLUE + Fore.CYAN,
Back.BLUE + Fore.WHITE,
Back.BLUE + Style.BRIGHT + Fore.RED,
Back.BLUE + Style.BRIGHT + Fore.GREEN,
Back.BLUE + Style.BRIGHT + Fore.YELLOW,
Back.BLUE + Style.BRIGHT + Fore.BLUE,
Back.BLUE + Style.BRIGHT + Fore.MAGENTA,
Back.BLUE + Style.BRIGHT + Fore.CYAN,
Back.BLUE + Style.BRIGHT + Fore.WHITE,

Back.WHITE + Fore.RED,
Back.WHITE + Fore.YELLOW,
Back.WHITE + Fore.MAGENTA,
#Back.WHITE + Style.BRIGHT + Fore.RED,
#Back.WHITE + Style.BRIGHT + Fore.YELLOW,
#Back.WHITE + Style.BRIGHT + Fore.BLUE,

Back.YELLOW + Fore.RED,
Back.YELLOW + Fore.BLUE,
#Back.YELLOW + Fore.MAGENTA,
#Back.YELLOW + Fore.CYAN,
Back.YELLOW + Fore.WHITE,
Back.YELLOW + Style.BRIGHT + Fore.WHITE,

Back.RED + Fore.GREEN,
Back.RED + Fore.CYAN,
Back.RED + Fore.WHITE,
Back.RED + Style.BRIGHT + Fore.GREEN,
Back.RED + Style.BRIGHT + Fore.YELLOW,
Back.RED + Style.BRIGHT + Fore.BLUE,
Back.RED + Style.BRIGHT + Fore.MAGENTA,
Back.RED + Style.BRIGHT + Fore.CYAN,
Back.RED + Style.BRIGHT + Fore.WHITE,

Back.BLACK + Fore.RED,
Back.BLACK + Fore.GREEN,
Back.BLACK + Fore.YELLOW,
Back.BLACK + Fore.BLUE,
Back.BLACK + Fore.MAGENTA,
Back.BLACK + Fore.CYAN,
Back.BLACK + Fore.WHITE,
Back.BLACK + Style.BRIGHT + Fore.RED,
Back.BLACK + Style.BRIGHT + Fore.GREEN,
Back.BLACK + Style.BRIGHT + Fore.YELLOW,
Back.BLACK + Style.BRIGHT + Fore.BLUE,
Back.BLACK + Style.BRIGHT + Fore.MAGENTA,
Back.BLACK + Style.BRIGHT + Fore.CYAN,
Back.BLACK + Style.BRIGHT + Fore.WHITE,
]
nice_colors_num = len( nice_colors)
import binascii

def crc_colorize( s):
    crc = binascii.crc_hqx( s.encode('ascii'), 0)
    #print( s, crc, crc % nice_colors_num)
    return( nice_colors[ crc % nice_colors_num] + s + Style.RESET_ALL)

for i in nice_colors:
    print( i + "Some text that is supposed to be readable" + Style.RESET_ALL)

for a in all_adds:
    print( 'Add:', crc_colorize( a))

for b in all_broadcasts:
    print( 'Broadcast:', crc_colorize( b))


print(Style.RESET_ALL)
print('back to normal now')

cmd = ['/sbin/tcpdump', '-qlni', 'eth0']



import re

import time
import queue
import sys
import threading
import subprocess
PIPE = subprocess.PIPE


"""
hex = qr/[0-9a-f]/;
fqdn = qr/(?:[A-Za-z\d\-\.]+\.[a-z]+)/;
#my $ipv4_addr = qr/(?:(?:\d{1,3}\.){3}\d{1,3})/;
ipv4_addr = qr/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/;
ipv6_grp = qr/$hex{1,4}/;
ipv6_addr = qr/(?:::)?(?:${ipv6_grp}::?)+${ipv6_grp}(?:::)?/;
ipv6_rev = qr/(?:(?:$hex\.){31}$hex)/;
ipv6_addr = qr/(?:$ipv6_addr|$ipv6_rev)/;
port = qr/(?:\d{1,5}|[a-z\d\-\.]+)/;

>>> def dashrepl(matchobj):
...     if matchobj.group(0) == '-': return ' '
...     else: return '-'
>>> re.sub('-{1,2}', dashrepl, 'pro----gram-files')
'pro--gram files'
>>> re.sub(r'\sAND\s', ' & ', 'Baked Beans And Spam', flags=re.IGNORECASE)
'Baked Beans & Spam'
"""

fqdn = r'(?:[A-Za-z\d\-\.]+\.[a-z]+)';
#my $ipv4_addr = qr/(?:(?:\d{1,3}\.){3}\d{1,3})/;
ipv4_addr = r'(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
# numeric or resolved port names:
port = r'(?:\d{1,5}|[a-z\d\-\.]+)'
hexre = '[0-9a-f]'
ipv6_grp = hexre+'{1,4}';
ipv6_addr = '(?:::)?(?:'+ipv6_grp+'::?)+'+ipv6_grp+'(?:::)?'
#ipv6_addr = '(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))'

ipv6_addr = '(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9]))'
#ipv6_addr = 

proto = '[A-Z]{1,8}' # is 8 enough?
#ipv6_rev = qr/(?:(?:$hex\.){31}$hex)/;
#ipv6_addr = qr/(?:$ipv6_addr|$ipv6_rev)/;

from pprint import pprint

from geolite2 import geolite2
reader = geolite2.reader()

"""
>>> from geolite2 import geolite2
>>>
>>> reader = geolite2.reader()
>>> reader.get('1.1.1.1')
{'country': ... }
>>>
>>> geolite2.close()
#pprint(vars(object))
"""

ranges_info = {
    'RFC1918': { 
        '10.0.0.0/8': 'A',
        '172.16.0.0/12': 'B',
        '192.168.0.0/16': 'C'
    },
    'MCAST':
    {
        '224.0.0.1/32': 'hosts',
        '224.0.0.2/32': 'routers',
        '224.0.0.4/32': 'DVMRP',
        '224.0.0.5/32': 'OSPF',
        '224.0.0.6/32': 'OSPFDR',
        '224.0.0.9/32': 'RIP2',
        '224.0.0.10/32': 'EIGRP',
        '224.0.0.13/32': 'PIM',
        '224.0.0.18/32': 'VRRP',
        '224.0.0.19/32': 'IS-ISoIP',
        '224.0.0.20/32': 'IS-ISoIP',
        '224.0.0.21/32': 'IS-ISoIP',
        '224.0.0.22/32': 'IGMP',
        '224.0.0.102/32': 'HSRPv2',
        '224.0.0.107/32': 'PTP',
        '224.0.0.251/32': 'mDNS',
        '224.0.0.252/32': 'LLMNR',
        '224.0.0.253/32': 'Teredo',
        '224.0.1.1/32': 'NTP',
        '224.0.1.22/32': 'SLP',
        '224.0.1.35/32': 'SLP',
        '224.0.1.39/32': 'CISCO-ANNOUNCE',
        '224.0.1.40/32': 'CISCO-DISCOVER',
        '224.0.1.41/32': 'H.323GK',
        '224.0.1.128/30': 'PTP',
        '239.255.255.250/32': 'SSD',
        '239.255.255.253/32': 'SLP',
        'ff02::1': 'hosts',
        'ff02::2': 'routers',
        'ff02::5': 'OSPF',
        'ff02::6': 'OSPFDR',
        'ff02::9': 'RIP2',
        'ff02::a': 'EIGRP',
        'ff02::d': 'PIM',
        'ff02::12': 'VRRP',
        'ff02::8': 'IS-ISoIP',
        'ff02::16': 'MLDv2',
        'ff02::1:2': 'DHCPv6',
        'ff00::fb/128': 'mDNS',
        'ff01::fb/128': 'mDNS',
        'ff02::fb/128': 'mDNS',
        'ff03::fb/128': 'mDNS',
        'ff04::fb/128': 'mDNS',
        'ff02::1:3': 'LLMNR',
        'ff05::1:3': 'DHCP',
        'ff00::101': 'NTP',
        'ff01::101': 'NTP',
        'ff02::101': 'NTP',
        'ff03::101': 'NTP',
        'ff00::181/128': 'PTP-MSG',
        'ff01::181/128': 'PTP-MSG',
        'ff02::181/128': 'PTP-MSG',
        'ff03::181/128': 'PTP-MSG',
        'ff02::6b/128': 'PTP-PD',
        'ff00::c/128': 'SSDP',
        'ff01::c/128': 'SSDP',
        'ff02::c/128': 'SSDP',
        'ff03::c/128': 'SSDP'
    }
}

# importing the module
import json

# Opening JSON file
with open('data/ctd-data.json') as json_file:
    data = json.load(json_file)
    for key,value in data.items():
        print(key)
        ranges_info[ key] = data[ key]
    pprint( ranges_info)


import ipaddress



def get_ip_info( ip):
    info = ''
    geoip = reader.get( ip)
    if geoip != None:
        #pprint(geoip)
        info += crc_colorize(geoip['country']['iso_code'])
        if 'subdivisions' in geoip:
            info += '/' + crc_colorize(geoip['subdivisions'][0]['iso_code'])

    if info != "":
        info = f'[{info}]'

    for descr in ranges_info.keys():
        moreinfo = ""
        #print( 'descr: ', descr)
        for r in ranges_info[ descr].keys():
            #pprint( r)
            found=False
            if ':' in ip and ':' in r:
                if ipaddress.IPv6Address( ip) in ipaddress.IPv6Network(r):
                    found=True
            elif ':' not in ip and ':' not in r:
                if ipaddress.IPv4Address( ip) in ipaddress.IPv4Network(r):
                    found=True
#            if ip.search('\.') and ipaddress.IPv4Address( ip) in ipaddress.IPv4Network(r)
#            or ipaddress.IPv6Address( ip) in ipaddress.IPv6Network(r):
                #print( 'ip is in net', ip, r)
            if found:
                if moreinfo == "":
                    moreinfo = crc_colorize( descr)
                if ranges_info[ descr][ r] != "":
                    moreinfo += '/' + crc_colorize( ranges_info[ descr][ r])
        if moreinfo != "":
            info += f'[{moreinfo}]'

    #  TODO : implement caching update and checking at the beginning
    if info != "":
        return " " + info
    return ""

def colorize_match_ip( matchobj):
    return crc_colorize( matchobj.group(1)) + get_ip_info(matchobj.group(1))

def colorize_match_ip_port( matchobj):
    #print ( f'asked to colorize: {matchobj.group(0)}/{matchobj.group(1)}/{matchobj.group(2)}]' )
    return crc_colorize( matchobj.group(1)) + ':' + crc_colorize( matchobj.group(2)) + get_ip_info(matchobj.group(1))

def colorize_match( matchobj):
    return crc_colorize( matchobj.group(1))

def prettify_tcpdump_line_so_it_looks_nice( line):
    #print( "old:  ", line)
    for add in all_adds:
        if re.search( ' > ' + add + f'(:|\.{port})', line):
            #print( "LOCAL on the right found")
            line = re.sub( '\s('+proto+')\s(.*) > (.*?):\s', ' \g<1> \g<3> < \g<2>: ', line)

    for add in all_broadcasts:
        if re.search( ' > ' + add + f'(:|\.{port})', line):
            print( "BROADCAST found")
            line = re.sub( f'^([0-9:\.]+\s{proto})\s({ipv4_addr})(\s|:|\.)', 
                f' \g<1> {Back.BLACK}{Style.BRIGHT}{Fore.YELLOW}(({Style.RESET_ALL}'
                + f'\g<2>{Back.BLACK}{Style.BRIGHT}{Fore.YELLOW})){Style.RESET_ALL}'
                + '\g<3>', line)

    #line = re.sub( ipv4_addr, colorize_match, line)
    # Fix time, also so that it doesn't get recognised as ipv6 :D
    # Also why does \d{2} not work in the second etc groupings?!?
    line = re.sub( '^(\d{2}):(\d{2}):(\d{2})\.(\d{3})\d+\s', '\g<1>\g<2>\g<3>.\g<4> ', line)
    #line = re.sub( '^(\d{2}):(\d+):\d', 'ABC', line)


    if re.search( ' IP .*: (?:tcp |UDP,)', line):
        line = re.sub( f'({ipv4_addr})\.({port})', colorize_match_ip_port, line)
    elif re.search( ' IP6 .*: (?:tcp |UDP,)', line):
        line = re.sub( f'({ipv6_addr})\.({port})', colorize_match_ip_port, line)
    elif re.search( ': ICMP ', line):
        line = re.sub( f'({ipv4_addr})', colorize_match_ip, line)
        line = re.sub( '(ICMP echo request)', f'{Back.BLACK}{Fore.GREEN}\g<1>{Style.RESET_ALL}', line)
        line = re.sub( '(ICMP echo reply)', f'{Back.BLACK}{Style.BRIGHT}{Fore.GREEN}\g<1>{Style.RESET_ALL}', line)
       
    elif re.search( ': ICMP6 ', line):
        line = re.sub( f'({ipv6_addr})', colorize_match_ip, line)
    elif re.search( ' ARP', line):
        # ARP, Request who-has 172.30.253.88 (00:15:5d:0f:f3:ba) tell 172.30.240.1, length 28
        line = re.sub( ', Request who-has (.*?) tell (.*?),', 
                 f' {Back.BLACK}{Style.BRIGHT}{Fore.YELLOW}(({Style.RESET_ALL}'
                + f'\g<2>{Back.BLACK}{Style.BRIGHT}{Fore.YELLOW})){Style.RESET_ALL}'
                + f' who-has \g<1>'
            , line)
        # ARP, Reply 172.30.253.88 is-at 00:15:5d:0f:f3:ba, length 28
        line = re.sub( ', Reply (.*?) is-at (.*?),', f' \g<1> reply: \g<2>', line)
        line = re.sub( f'({ipv4_addr})', colorize_match, line)
    else:
        line = re.sub( f'({ipv4_addr})', colorize_match, line)

    line = re.sub( ' > ', Back.BLACK + Style.BRIGHT + Fore.RED  + ' > ' + Style.RESET_ALL, line)
    line = re.sub( ' < ', Back.BLACK + Style.BRIGHT + Fore.BLUE + ' < ' + Style.RESET_ALL, line)
    #print( "nice: ", line)

    print( line)
    

def read_stderr(pipe, funcs):
    for line in iter(pipe.readline, ''):
        for func in funcs:
            func( (True, line))
            # time.sleep(1)
    pipe.close()

def read_output(pipe, funcs):
    for line in iter(pipe.readline, ''):
        for func in funcs:
            func( (False, line))
            # time.sleep(1)
    pipe.close()

def write_output(get):
    for isStderr, line in iter(get, None):
        #sys.stdout.write(line.decode("utf-8"))
        if isStderr:
            print( 'stderr', line.rstrip().decode("utf-8"))
        else:
            prettify_tcpdump_line_so_it_looks_nice( line.rstrip().decode("utf-8"))

process = subprocess.Popen(
    cmd, stdout=PIPE, stderr=PIPE, close_fds=True, bufsize=1)
q = queue.Queue()

tout = threading.Thread(
    target=read_output, args=(process.stdout, [q.put]))
terr = threading.Thread(
    target=read_stderr, args=(process.stderr, [q.put]))
twrite = threading.Thread(target=write_output, args=(q.get,))

for t in (tout, terr, twrite):
    t.daemon = True
    t.start()

process.wait()

for t in (tout, terr):
    t.join()

q.put(None)


