#!/usr/bin/env python3

### Default values
debug = False
nocolor=False
detectlocal = False

### Nice help text
usage_text_short ="""
    Usage: ./ctd [CTD-OPTION] ... [TCPDUMPLIKE-COMMAND + arguments]
    E.g.   ./ctd tcpdump -lni eth0

    --help  Display more help
"""
usage_text_full = r"""

    Welcome to Colorful tcpdump!

    Usage: ./ctd [CTD-OPTION] ... [ --info IP | TCPDUMPLIKE-COMMAND + arguments]
        CTD-OPTION: [ --indent INT] [ --detect-local-from-input ]
        TCPDUMPLINE-COMMAND: [ - / tcpdump / pktmon / tshark / traceroute / sshuttle / ...]

    Available CTD-OPTIONs: (NYI: Not Yet Implemented)

    --info <IP>
        Display what is known about this IP and exit

    --indent INT (NYI)
    -i INT
        indent allput by INT spaces. This allows you to run one ctd in
        the background (e.g. with the & operater in bash), for 
        instance listening on eth0. Then when you open a VPN tunnel,
        run ctd in the foreground with an indent of 4. This should give
        a nice output of external & internal traffic.

    --myip-override IP (or 'IP1 IP2 IP3')
        Manually set another IP(s) to be considered 'local', which will
        be placed on the left in CTD's output.

    --detect-local-from-input
    -d
        If you run ctd for example throgh a pipe from another systen,
        be it an ssh command run elsewhere, or on windows while ctd runs
        inside WSL, then ctd's local IPs detection won't make sense.
        Prepend the relevant command for your OS to the tcpdump command
        for ctd to pick up those local IPs instead of letting it try to
        do that itself. Commands that will be supported include:
        ifconfig, ip adddr and  ipconfig /all.
        Examples:
        1.
        Running pktmon.exe from WSL (need to start WSL as Administrator
        to be able to do this):
        WSL-bash$ { C:\Windows\system32\ipconfig.exe /all; PktMon.exe start -c --comp nics -m real-time } | ./ctd --detect-local-from-input
        2.
        Running tcpdump on a remote host and piping the output back via ssh:
        bash$ ssh root@ubuntu "ip addr; tcpdump -lni eth0" | ./ctd --detect-local-from-input

    --debug LEVEL
        Also show the original lines before they were mangled by CTD  o_O
        LEVEL can be 1 to 5, the higher, the more verbose

    More examples:
        ./ctd tcpdump -lni eth0
        ./ctd --info 140.82.121.4
        ./ctd /mnt/c/Windows/System32/PktMon.exe start -c --comp nics -m real-time (In WSL running as Administrator)
        ./ctd C:\Windows\system32\PktMon.exe start -c --comp nics -m real-time (In native windows running as Administrator)

    """

ctd_logo = """
   ,o888888o.       ,o888888o.     88888        ,o888888o.     8888888888o.   88888888888   88888      88 88888         
  8888     `88.   .8888     `88.   88888      .8888     `88.   88888    `88.  88888         88888      88 88888         
,88888       `8. ,88888       `8b  88888     ,88888       `8b  88888     `88  88888         88888      88 88888         
888888           888888        `8b 88888     888888        `8b 88888     ,88  88888         88888      88 88888         
888888           888888         88 88888     888888         88 88888.   ,88'  888888888     88888      88 88888         
888888           888888         88 88888     888888         88 8888888888P'   88888         88888      88 88888         
888888           888888        ,8P 88888     888888        ,8P 88888`8b       88888         88888      88 88888         
`88888       .8' `88888       ,8P  88888     `88888       ,8P  88888 `8b.     88888         `8888     ,8P 88888         
  8888     ,88'   `8888     ,88'   88888      `8888     ,88'   88888   `8b.   88888          8888   ,d8P  88888         
   `8888888P'       `8888888P'     888888888888 `8888888P'     88888     `88. 88888           `Y88888P'   8888888888888 

# ## ### #### ##### ###### ####### # ## ### #### ##### ###### ####### # ## ### #### ##### ###### ####### # ## ### ####
####### ###### ##### #### ### ## # ####### ###### ##### #### ### ## # ####### ###### ##### #### ### ## # ####### ######

888888888888888 ,o888888o.    8888888888o   8888888888o.      88888      88        ,8.       ,8.          8888888888o    
      8888     8888     `88.  88888    `88. 88888    `^888.   88888      88       ,888.     ,888.         88888    `88.  
      8888   ,88888       `8. 88888     `88 88888        `88. 88888      88      .`8888.   .`8888.        88888     `88  
      8888   888888           88888     ,88 88888         `88 88888      88     ,8.`8888. ,8.`8888.       88888     ,88  
      8888   888888           88888.   ,88' 88888          88 88888      88    ,8'8.`8888,8^8.`8888.      88888.   ,88'  
      8888   888888           8888888888P'  88888          88 88888      88   ,8' `8.`8888' `8.`8888.     8888888888P'   
      8888   888888           88888         88888         ,88 88888      88  ,8'   `8.`88'   `8.`8888.    88888          
      8888   `88888       .8' 88888         88888        ,88' `8888     ,8P ,8'     `8.`'     `8.`8888.   88888          
      8888     8888     ,88'  88888         88888    ,o88P'    8888   ,d8P ,8'       `8        `8.`8888.  88888          
      8888      `8888888P'    88888         8888888888P'        `Y88888P' ,8'         `         `8.`8888. 88888

# ## ### #### ##### ###### ####### # ## ### #### ##### ###### ####### # ## ### #### ##### ###### ####### # ## ### ####
####### ###### ##### #### ### ## # ####### ###### ##### #### ### ## # ####### ###### ##### #### ### ## # ####### ######
"""

### Set up everything to do with colours
import colorsys
import itertools
import re

def zenos_dichotomy():
    for k in itertools.count():
        yield 1/2**k

def fracs():
    yield 0
    for k in zenos_dichotomy():
        i = int(round(1/k)) # dyadic denominators: 1, 2, 4, 8, ... (was float, which range() rejects on Python 3)
        for j in range(1,i,2):
            yield j/i

def hue_to_tones(h):
    for s in [0.6]:
        for v in [0.8, 0.7]:
            yield (h, s, v)

def hsv_to_rgb(x):
    return colorsys.hsv_to_rgb(*x)

flatten = itertools.chain.from_iterable

def hsvs():
    return flatten(map(hue_to_tones, fracs()))

def rgbs():
    return map(hsv_to_rgb, hsvs())

def rgb_to_css(x):
    t = tuple(map(lambda y: int(y*255), x))
    tup = list(t) + [0]
    if (0.299 * tup[0] + 0.587 * tup[1] + 0.114 * tup[2])/255 > 0.5:
        tup[3] = 1
    return tup

def css_colors():
    return map(rgb_to_css, rgbs())

def rainbowColor( percent_x2):
    # Based on: https://github.com/gnachman/iTerm2/blob/master/tests/24-bit-color.sh
    h = int(percent_x2 / 43)
    f = int(percent_x2 - 43 * h)
    t = int(f * 255 / 43)
    q = 255 - t
    if h == 0:
        rgb = ( 255, t, 0)
    elif h == 1:
        rgb = ( q, 255, 0)
    elif h == 2:
        rgb = ( 0, 255, t)
    elif h == 3:
        rgb = ( 0, q, 255)
    elif h == 4:
        rgb = ( t, 0, 255)
    elif h == 5:
        rgb = ( 255, 0, q)
    
    tup = list(rgb) + [0]
    if (0.299 * tup[0] + 0.587 * tup[1] + 0.114 * tup[2])/255 > 0.5:
      tup[3] = 1
    return tup

sample_colors = list(itertools.islice(css_colors(), 100))

#pprint(sample_colors)

from colorama import *
init()
"""
Available formatting constants are:
Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
Style: DIM, NORMAL, BRIGHT, RESET_ALL
"""
Z_FORE = 38
Z_BACK = 48

def rgb_ansi( color_tuple, z_level=Z_FORE):

#def _e(red_component, green_component, blue_component, z_level=Z_FORE):
    """Return escaped color sequence"""
    z_level = Z_BACK

    ansi = '\x01\x1b[{};2;{};{};{}m\x02'.format(
        Z_BACK, color_tuple[0], color_tuple[1], color_tuple[2])

    if color_tuple[3] == 1:
        ansi += Style.BRIGHT + Fore.WHITE
    elif color_tuple[3] == 0:
        ansi += '\x01\x1b[{};2;{};{};{}m\x02'.format( 
        Z_FORE, 0,0,0)
    elif color_tuple[3] == 2:
        ansi = '\x01\x1b[{};2;{};{};{}m\x02'.format(
          Z_FORE, color_tuple[0], color_tuple[1], color_tuple[2])
        ansi += '\x01\x1b[{};2;{};{};{}m\x02'.format( 
          Z_BACK, 0,0,0)
        

    return ansi

#    return '\x01\x1b[{};2;{};{};{}m\x02'.format(
#        z_level, color_tuple[0], color_tuple[1], color_tuple[2], front_color)
#print( f'{rgb_ansi( (140,230,215))}Testing4')





import binascii

nice_colors = sample_colors
for col in list(sample_colors):
  c = list(col)
  c[3] = 2
  nice_colors += [ (c[0], c[1], c[2], c[3]) ]


nice_colors_num = len( nice_colors)

#print( nice_colors)

def crc_colorize( s):
    if nocolor:
      return( s)
    else:
      crc = binascii.crc_hqx( s.encode('ascii'), 0)
      #print( s, crc, crc % nice_colors_num)
      #return( nice_colors[ crc % nice_colors_num] + s + Style.RESET_ALL)
      return( rgb_ansi( nice_colors[ crc % nice_colors_num]) + s + Style.RESET_ALL)

def colorize_match( matchobj):
    return crc_colorize( matchobj.group(1))

# IPv6 family colours: restrict the stable CRC palette to the cool
# (blue-dominant) half so IPv6 addresses are recognisable by temperature.
# Link-local fe80:: addresses get dimmed: ubiquitous and rarely interesting.
cool_colors = [c for c in sample_colors if c[2] > c[0]]

def crc_colorize_cool( s):
    if nocolor:
      return( s)
    crc = binascii.crc_hqx( s.encode('ascii'), 0)
    return rgb_ansi( cool_colors[ crc % len( cool_colors)]) + s + Style.RESET_ALL

import random
### Replace different strings of length 1, 2 .., with the following words:
tcpdump_logo_strings = [ [], ['>', '+', '.', ':', '<'],
    ['::', 'A?', 'IP', 'CF', 'US', 'UK', 'AU', 'IE', 'NZ', 'NL', 'DE', 'FR', 'CA', 'CN', 'RU'],
    ['dns', 'ssh', 'AWS', 'UDP', 'tcp', 'IP6', 'TOR', 'ARP', 'EC2', 'VPN'],
    ['12'+random.choice('123456789')+'.', '23'+random.choice('123456789')+'.', '[S.]', 'MSFT', 'AAAA', 'http'],
    [ random.choice('abcdef')+'.com', random.choice('abcdef')+'.net', 'MCAST', 'AZURE', 'LLMNR', 'https'],
    ['200'+random.choice('1234567890abcdef')+'::', random.choice('1234567890abcdef')+'f::fb', 'AKAMAI', 'GOOGLE', 'GCLOUD', 'AMAZON'],
    ['RFC1918', '',''],
    ['', '',''],
    ['', '',''],
    ['', '',''],
    ['', '',''],
]

def gen_random_logo_strings( o):
    return random.choice( tcpdump_logo_strings[ len( o.group(0))])

def show_logo():
    colored_logo = ctd_logo
    
    colored_logo = re.sub( r'([^\s]{1,6})', gen_random_logo_strings, colored_logo)
    colored_logo = re.sub( r'([^\s]{1,6})', colorize_match, colored_logo)

    print( colored_logo)
    print()
    # Colorize URL parts semantically: scheme, ://, domain, user, repo
    link = 'GitHub: https://github.com/ejtaal/colorful-tcpdump'
    def color_url_part(m):
        return crc_colorize(m.group(0))
    link = re.sub(r'https', color_url_part, link)          # scheme
    link = re.sub(r'://', color_url_part, link)            # separator
    link = re.sub(r'github\.com', color_url_part, link)    # domain
    link = re.sub(r'ejtaal', color_url_part, link)         # username
    link = re.sub(r'colorful-tcpdump', color_url_part, link)  # repo
    print( link)

import argparse
parser = argparse.ArgumentParser( description='A script to prettify tcpdump output with colours, add extra info regarding IPs seen, and add some other enhancements to the output.')

group = parser.add_mutually_exclusive_group( required=True)
group.add_argument( '--info', metavar='IP', type=str, nargs=1, help='Tell me what you know about this IP and then quit.')
group.add_argument( 'read', metavar='TCPDUMP_LIKE_CMD',  type=str, nargs='?', help='The command to run, from which output is read and colorized. This is assumed to be tcpdump or similar (support for others is TODO)')

parser.add_argument( '-d', '--detect-local-from-input', action='store_true', help='Do not detect local interfaces in code, but detect them from running e.g. `ip addr` prior to the tcpdump command. This is useful for when output is read from a remote ssh tcpdump command instead of a locally running one, e.g. `./ctd -d ssh user@remotehost "ip addr; tcpdump -qlni eth0"`')
parser.add_argument( '-w', "--wrap", help="Wrap long lines. Default is to cut lines that don't fit in the terminal", action="store_true")
parser.add_argument( '--nocolor', action='store_false', help='Do away with all the eye candy colors!. Use this in scripts when you just want to capture plain text info without all the ANSI color sequences.')
parser.add_argument( '-nl', "--nologo", help="Skip showing the super cool logo", action="store_true")
# Note! dashes are converted into underscores else it's not valid python! So it becomes args.myip_override
parser.add_argument( '--myip-override', metavar='IP', type=str, nargs=1, help='set a local IP manually')

parser.add_argument( '--debug', action='store_true', help='Print way more debugging info.')
parser.add_argument( '--no-pids', action='store_true', help='Disable process identification (the [proc:pid] tags on each line).')

args = parser.parse_args()

if not args.nologo and not args.info:
  show_logo()

if args.debug:
  debug = True

if args.nocolor is False:
  nocolor = True

if args.detect_local_from_input:
    detectlocal = True

pids_enabled = not args.no_pids

### Get local interface addresses

all_adds = []
all_broadcasts = []


if debug:
    print( args.myip_override)
if args.myip_override:
    all_adds = args.myip_override.split(',')
else:
    from netifaces import *
    # TODO: detect running on windows and detect IPs there the right way(tm)
    for ifaceName in interfaces():
        #all_ifs.append( ifaddresses(ifaceName))
        for key, value in ifaddresses(ifaceName).items():
            #print(key, '->', value)
            pass  # all_ifs removed; no longer used
            if 'addr' in value[0]:
                #print( 'addr', value[0]['addr'])
                if value[0]['addr'] not in all_adds:
                    all_adds.append( value[0]['addr'])
            if 'broadcast' in value[0]:
                #print( 'broadcast', value[0]['broadcast'])
                if value[0]['broadcast'] not in all_broadcasts:
                    all_broadcasts.append( value[0]['broadcast'])


if debug:
    print( 'Our network addresses (will be placed on the left):')
    for a in all_adds:
        print( crc_colorize( a) + ' ', end='')
    print('')

    print( 'Local broadcast addresses:')
    for b in all_broadcasts:
        print( crc_colorize( b) + ' ', end='')
    print('')



import time
import queue
import sys
import threading
import subprocess
PIPE = subprocess.PIPE
import os

if debug:
  print("Argument List:", str(sys.argv))

#cmd = ['/sbin/tcpdump', '-qlni', 'eth0']
cmd = sys.argv


fqdn = r'(?:[A-Za-z\d\-\.]+\.[a-z]+)';
ipv4_addr = r'(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
# numeric or resolved port names:
port = r'(?:\d{1,5}|[a-z\d\-\.]+)'
hexre = '[0-9a-f]'
ipv6_grp = f'{hexre}{1,4}';
ipv6_addr = f'(?:::)?(?:{ipv6_grp}::?)+{ipv6_grp}(?:::)?'
#ipv6_addr = '(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))'

ipv6_addr = r'(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9]))'

proto = '[A-Z]{1,8}' # is 8 enough?

from data.ip2asn_lookup import geolite2
reader = geolite2.reader()

"""
>>> from data.ip2asn_lookup import geolite2
>>>
>>> reader = geolite2.reader()
>>> reader.get('1.1.1.1')
{'country': ... }
>>>
>>> geolite2.close()
#pprint(vars(object))
"""

# A bit like an example of how this array is built
ranges_info = {
    'RFC1918': [
        ['10.0.0.0/8', 'A'],
        ['172.16.0.0/12', 'B'],
        ['192.168.0.0/16', 'C']
    ],
    'MCAST': [
        ['224.0.0.1/32', 'hosts'],
        ['224.0.0.2/32', 'routers'],
        ['224.0.0.4/32', 'DVMRP'],
        ['224.0.0.5/32', 'OSPF'],
        ['224.0.0.6/32', 'OSPFDR'],
        ['224.0.0.9/32', 'RIP2'],
        ['224.0.0.10/32', 'EIGRP'],
        ['224.0.0.13/32', 'PIM'],
        ['224.0.0.18/32', 'VRRP'],
        ['224.0.0.19/32', 'IS-ISoIP'],
        ['224.0.0.20/32', 'IS-ISoIP'],
        ['224.0.0.21/32', 'IS-ISoIP'],
        ['224.0.0.22/32', 'IGMP'],
        ['224.0.0.102/32', 'HSRPv2'],
        ['224.0.0.107/32', 'PTP'],
        ['224.0.0.251/32', 'mDNS'],
        ['224.0.0.252/32', 'LLMNR'],
        ['224.0.0.253/32', 'Teredo'],
        ['224.0.1.1/32', 'NTP'],
        ['224.0.1.22/32', 'SLP'],
        ['224.0.1.35/32', 'SLP'],
        ['224.0.1.39/32', 'CISCO-ANNOUNCE'],
        ['224.0.1.40/32', 'CISCO-DISCOVER'],
        ['224.0.1.41/32', 'H.323GK'],
        ['224.0.1.128/30', 'PTP'],
        ['239.255.255.250/32', 'SSD'],
        ['239.255.255.253/32', 'SLP'],
        ['ff02::1', 'hosts'],
        ['ff02::2', 'routers'],
        ['ff02::5', 'OSPF'],
        ['ff02::6', 'OSPFDR'],
        ['ff02::9', 'RIP2'],
        ['ff02::a', 'EIGRP'],
        ['ff02::d', 'PIM'],
        ['ff02::12', 'VRRP'],
        ['ff02::8', 'IS-ISoIP'],
        ['ff02::16', 'MLDv2'],
        ['ff02::1:2', 'DHCPv6'],
        ['ff00::fb/128', 'mDNS'],
        ['ff01::fb/128', 'mDNS'],
        ['ff02::fb/128', 'mDNS'],
        ['ff03::fb/128', 'mDNS'],
        ['ff04::fb/128', 'mDNS'],
        ['ff02::1:3', 'LLMNR'],
        ['ff05::1:3', 'DHCP'],
        ['ff00::101', 'NTP'],
        ['ff01::101', 'NTP'],
        ['ff02::101', 'NTP'],
        ['ff03::101', 'NTP'],
        ['ff00::181/128', 'PTP-MSG'],
        ['ff01::181/128', 'PTP-MSG'],
        ['ff02::181/128', 'PTP-MSG'],
        ['ff03::181/128', 'PTP-MSG'],
        ['ff02::6b/128', 'PTP-PD'],
        ['ff00::c/128', 'SSDP'],
        ['ff01::c/128', 'SSDP'],
        ['ff02::c/128', 'SSDP'],
        ['ff03::c/128', 'SSDP']
    ]
}

# IPv6 broadcast stuff with local reply?
#164155.070 IP6 fe80::ffff:ffff:ffff:ffff > ff02::1: HBH ICMP6, multicast listener queryv2  [gaddr ::], length 28
#164155.079 IP6 fe80::250:56ff:fe86:e146 > ff02::16: HBH ICMP6, multicast listener report v2, 1 group record(s), length 28


# importing the module
import json
import radix

rtree = radix.Radix()

# Opening JSON file
if debug:
  print("Loading range data...")
with open('data/ctd-data.json') as json_file:
    data = json.load(json_file)
    # Merge JSON entries into ranges_info so the radix tree picks up BOTH
    # the hardcoded ranges (RFC1918, MCAST defined above) and the JSON-defined
    # ones. Previously only data.items() was iterated, so RFC1918 and MCAST
    # were never inserted into the radix tree and lookups silently missed
    # them at runtime (e.g. 192.168.x.x IPs got no [RFC1918/C] tag).
    ranges_info.update(data)
    for key,value in ranges_info.items():
        if debug:
          print( key + ' ', end='')
        for subnet,info in ranges_info[ key]:
            # if debug:
            #     print( f"{key}: {subnet}/{info}")
            # # Adding a node returns a RadixNode object. You can create
            # # arbitrary members in its 'data' dict to store your data
            # rnode = rtree.add("10.0.0.0/8")
            # rnode.data["blah"] = "whatever you want"
            # if subnet == '146.59.44.45/32':
            #     continue

            rnode = rtree.search_exact( subnet)
            if rnode:
                # print('Seen already: ', rnode.data)
                if key in rnode.data:
                    if info in rnode.data[ key]:
                        continue
                    else:
                        rnode.data[ key].append( info)
                else:
                    rnode.data[key] = [info]
                    # print( rnode.data)
                # if subnet == "146.59.0.0/16":
                #     print( rnode.data)
                #     # exit(7)
            else:
                # Not present yet, adding it
                rnode = rtree.add( subnet)
                rnode.data[key] = [info]

            # if subnet == "146.59.0.0/16":
            #     print( rnode.prefix)
            #     print( rnode.data)
                # exit(7)
            
    # exit(9)

    #pprint( ranges_info)
if debug:
  print('')
  print("Done")

import ipaddress

### Process identification (optional, requires psutil)
process_map = {}  # (local_ip, local_port) -> (process_name, pid)
_process_stop = threading.Event()

def _poll_process_map():
    """Background thread: periodically build a map of (local_ip, port) -> (process, pid)."""
    try:
        import psutil
    except ImportError:
        if debug:
            print("psutil not installed — process identification disabled.")
        return
    while not _process_stop.is_set():
        process_map.clear()
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.pid is None:
                    continue
                laddr = conn.laddr
                if not laddr or not laddr.ip:
                    continue
                try:
                    proc = psutil.Process(conn.pid)
                    process_map[(laddr.ip, laddr.port)] = (proc.name(), conn.pid)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except (psutil.AccessDenied, OSError):
            pass
        _process_stop.wait(1.5)

if pids_enabled:
  _process_thread = threading.Thread(target=_poll_process_map, daemon=True)
  _process_thread.start()
  print("[*] Process identification enabled (polling psutil every 1.5s)")

def _extract_source_addr(line):
    """Extract the source IP and port from the first packet on the line.
    Returns (ip, port_str) or (None, None).
    """
    # IPv4: "IP 10.0.0.5.52341 >"
    m = re.search(r'\bIP\s+(\d{1,3}(?:\.\d{1,3}){3})(\.\d+)\s*>', line)
    if m:
        return m.group(1), m.group(2)[1:]  # strip the leading '.'

    # IPv6 with bracket notation: "IP6 [2001:db8::1].8080 >"
    m = re.search(r'\bIP6\s+\[([^\]]+)\](\.\d+)\s*>', line)
    if m:
        return m.group(1), m.group(2)[1:]

    # IPv6 bare: "IP6 fe80::1.8080 >" — last colon-group of digits is the port
    m = re.search(r'\bIP6\s+([\da-fA-F:]+):(\d{1,5})\s*>', line)
    if m:
        return m.group(1), m.group(2)

    return None, None

# Ze great IP info cache
info_cache={}

def get_ip_info( ip):

    info = ''
    dnsinfo = ''

    if ip in dns_cache['by_ip']:
        dnsinfo = ' ' + crc_colorize( dns_cache['by_ip'][ip])

    if ip in info_cache:
        #print( 'CACHE HIT')
        return dnsinfo + " " + info_cache[ ip]
    #print( 'CACHE MISS')

    geoip = reader.get( ip)
    if geoip != None:
        #pprint(geoip)
        if 'country' in geoip:
            info += crc_colorize(geoip['country']['iso_code'])
        else:
            info += crc_colorize( '??')

        # Add subdivision (state/region) if available
        if 'subdivision' in geoip and geoip['subdivision']:
            info += '/' + crc_colorize(geoip['subdivision'][:10])

        # Add city if available
        if 'city' in geoip and geoip['city']:
            city = geoip['city']
            if isinstance(city, dict):
                city_name = city.get('names', {}).get('en', '')
            else:
                city_name = str(city)
            if city_name:
                info += '/' + crc_colorize(city_name[:15])

        # Add ASN info if available (ip2asn-combined.tsv provides this)
        if 'name' in geoip and geoip['name']:
            # Truncate ASN name to 6 chars
            asn_name = geoip['name'][:6]
            info += '/' + crc_colorize(asn_name)

    if info != "":
        info = f'[{info}]'

    # # Covered search will return all prefixes inside the given
    # # search term, as a list (including the search term itself,
    # # if present in the tree)
    # rnodes = rtree.search_covered("10.123.0.0/16")

    # Note: covered()  returns nodes that the search term covers or equals
    #       covering() returns nodes that encompass the search term or equal it
    rnodes = rtree.search_covering( ip)
    if rnodes:
        # First gather all data from the relevant nodes:
        moreinfo = {}
        for rnode in rnodes:
            if debug:
                print( rnode.prefix)
                print( rnode.data)
            for key in rnode.data:
                for value in rnode.data[key]:
                    # if value != '':
                    if key in moreinfo:
                        moreinfo[ key].append( value)
                    else:
                        moreinfo[ key] = [ value]

    # rnodes = rtree.search_covered( ip)
    # for rnode in rnodes:
    #     print( rnode.prefix)
    #     print( rnode.data)
        # print( 'moreinfo: ', moreinfo)

        # if len(moreinfo) > 0:
        for descr in moreinfo.keys():
            addinfo = crc_colorize( descr)
            seen = []
            for i in moreinfo[ descr]:
                #print( 'i: ', i)
                #print( 'seen: ', seen)
                #if i in seen:
                #    print('i in seen?')
                #else:
                #    print('i NOT in seen?')
                if i not in seen and i != "":
                    # Display RFC1918 as LAN
                    if descr == 'RFC1918':
                        addinfo = crc_colorize('LAN')
                    else:
                        addinfo += '/' + crc_colorize( i)
                    #print( 'addinfo: ', addinfo)
                seen += [i]
            info += f'[{addinfo}]'

        # print( 'info: ', info)
        # exit(8)

    # Don't look up this ip again
    info_cache[ip] = info

    if info != "":
        return dnsinfo + " " + info

    # Else nothing to report but DNS (if any found)
    return dnsinfo


dns_cache= {}
dns_cache['queries'] = {}
dns_cache['responses'] = {}
dns_cache['by_ip'] = {}



def store_dns_info( matchobj):
    """
02:28:21.105740 IP 172.30.253.88.(53418) > (1.1.1.1.53: 18184)+ A? (blah.com). (26)
02:28:21.177084 IP 172.30.253.88.40745 > 1.1.1.1.53: 25446+ AAAA? blah.com. (26)
    """
    key = matchobj.group(1) + matchobj.group(2)
    domain = matchobj.group(3)
    #print( f'store_dns() key: [{key}] domain: [{domain}]')
    dns_cache['queries'][key] = domain

def match_dns_info( matchobj):
    """
02:33:56.598637 IP (1.1.1.1.53) > 172.30.253.88.(40418): (909) 1/0/0 A (189.113.174.199) (42)
04:16:50.506404 IP 1.1.1.1.53 > 172.30.253.88.43389: 55004 2/0/0 CNAME HDRedirect-LB7-5a03e1c2772e1c9c.elb.us-east-1.amazonaws.com., A 3.223.115.185 (113)
04:21:35.711426 IP 172.30.240.1.53 > 172.30.253.88.47204: 20303- 5/0/0 CNAME github.github.io., A 185.199.109.153, A 185.199.108.153, A 185.199.110.153, A 185.199.111.153 (158)
04:32:36.555860 IP 172.30.240.1.53 > 172.30.253.88.51003: 5787- 6/0/0 A 74.6.231.21, A 74.6.143.25, A 74.6.231.20, A 98.137.11.164, A 98.137.11.163, A 74.6.143.26 (132)
    """
    # print("MARK")
    key = matchobj.group(2) + matchobj.group(1) + ': ' + matchobj.group(3)
    result = matchobj.group(4)
    #print( f'match_dns() key: [{key}] result: [{result}]')
    if key in dns_cache['queries']:
        domain = dns_cache['queries'][ key]
        if debug:
          print( f"GOT DNS MATCH: [{domain}] = [{result}]")
        if re.search( ", A", result):
            if debug:
              print(f"We got back multiple matches: {result}")
            results = re.sub( ', A+ ', ',', result)
            for r in results.split(','):
                if debug:
                  print(f"Storing: {r}")
                dns_cache['by_ip'][ r] = domain
        else:
            # Looks to be a response with a single IP only
            dns_cache['by_ip'][ result] = domain
        #pprint( dns_cache['by_ip'])


def colorize_match_ip( matchobj):
    return crc_colorize( matchobj.group(1)) + get_ip_info(matchobj.group(1))

def colorize_match_ip_port( matchobj):
    #print ( f'asked to colorize: {matchobj.group(0)}/{matchobj.group(1)}/{matchobj.group(2)}]' )
    return crc_colorize( matchobj.group(1)) + ':' + crc_colorize( matchobj.group(2)) + get_ip_info(matchobj.group(1))

def colorize_matches_within( matchobj):
    s = matchobj.group(0)
    #print('IN MATCHES')
    for m in matchobj.groups():
        s = s.replace( m, crc_colorize( m))
    
    return s

### TCP flag colours, e.g. "Flags [P.]" -> "[P.]"
# Key = what tcpdump shows between the brackets. Bare flag = normal tone,
# flag + '.' (ACK) = bright, mirroring the existing [S] / [S.] convention.
FLAG_COLORS = {
    'S':    f'{Back.BLACK}{Fore.GREEN}',                    # SYN (open)
    'S.':   f'{Back.BLACK}{Style.BRIGHT}{Fore.GREEN}',      # SYN/ACK
    '.':    f'{Back.GREEN}{Style.BRIGHT}{Fore.WHITE}',      # pure ACK
    'P':    f'{Back.GREEN}{Fore.WHITE}',                    # PSH
    'P.':   f'{Back.GREEN}{Fore.WHITE}',                    # PSH/ACK (data)
    'R':    f'{Back.RED}{Fore.WHITE}',                      # RST (reset)
    'R.':   f'{Back.RED}{Fore.WHITE}',                      # RST/ACK (closed port)
    'F':    f'{Back.BLACK}{Fore.BLUE}',                     # FIN (close)
    'F.':   f'{Back.BLACK}{Style.BRIGHT}{Fore.BLUE}',       # FIN/ACK
    'FP':   f'{Back.BLACK}{Style.BRIGHT}{Fore.MAGENTA}',    # PSH+FIN (last data)
    'FP.':  f'{Back.BLACK}{Style.BRIGHT}{Fore.MAGENTA}',
    'U':    f'{Back.BLACK}{Style.BRIGHT}{Fore.YELLOW}',     # URG (urgent)
    'E':    f'{Back.BLACK}{Fore.CYAN}',                     # ECN-Echo
    'W':    f'{Back.BLACK}{Fore.CYAN}',                     # ECN CWR
}

def colorize_flags( matchobj):
    # Deliberately do not re-emit 'Flags ' to keep the output terse
    flags = matchobj.group(2).strip( '[]')
    return FLAG_COLORS.get( flags, '') + '[' + flags + ']' + Style.RESET_ALL

### IPv6 family colour + L2 control-plane protocol colours
IP6_STYLE = f'{Back.BLACK}{Style.BRIGHT}{Fore.CYAN}'    # 'IP6' keyword: cyan = v6, vs warm green = v4
L2_STYLE  = f'{Back.BLACK}{Style.BRIGHT}{Fore.MAGENTA}' # L2 control-plane keywords (STP, CDP, UDLD, ...)

# L2/router control-plane traffic seen on the wire (all print their name in
# plain text in tcpdump output, so keyword colouring is enough):
L2_CONTROL_KEYWORDS = r'CDPv2|UDLDv1|RSTP|MSTP|STP|LLDP|VTP|DTP|PAgP|LACP|EAPOL|CDP|UDLD|PVST\+|MVRP|GVRP|Dot1x'

def ip6_dim_prefix( ip):
    return Style.DIM if ip.startswith( 'fe80') else ''

def colorize_match_ip6_port( matchobj):
    ip, port = matchobj.group(1), matchobj.group(2)
    return ip6_dim_prefix( ip) + crc_colorize_cool( ip) + ':' + crc_colorize( port) + get_ip_info( ip)

def colorize_match_ip6( matchobj):
    ip = matchobj.group(1)
    return ip6_dim_prefix( ip) + crc_colorize_cool( ip)

def rainbow_colorize_value( value, max_value, amplifier = 1):
    tup = rainbowColor( int(value) * 200 / max_value)
    if amplifier < 1:
       #Attenuate the values, will require recalc of foreground colour too
        tup[0] = int( amplifier * tup[0])
        tup[1] = int( amplifier * tup[1])
        tup[2] = int( amplifier * tup[2])
        tup[3] = 0
        if (0.299 * tup[0] + 0.587 * tup[1] + 0.114 * tup[2])/255 > 0.5:
          tup[3] = 1

    tup[3] = 2
    return tup

      

def colorize_timestamp( matchobj):
    # Rearrange like so: '\g<1>\g<2>\g<3>.\g<4> '
    #print( matchobj)
    color_tup1 = rainbow_colorize_value( matchobj.group(1), 23, 1)
    color_tup2 = rainbow_colorize_value( matchobj.group(2), 59, 1)
    color_tup3 = rainbow_colorize_value( matchobj.group(3), 59, 1)
    color_tup4 = rainbow_colorize_value( matchobj.group(4), 999, 1)
    #print( rgb_ansi( nice_colors[ crc % nice_colors_num]) + matchobj.group(1) + Style.RESET_ALL)
    return \
      rgb_ansi( color_tup1) + matchobj.group(1) +  \
      rgb_ansi( color_tup2) + matchobj.group(2) +  \
      rgb_ansi( color_tup3) + matchobj.group(3) + Style.RESET_ALL + \
      "." + \
      rgb_ansi( color_tup4) + matchobj.group(4) + Style.RESET_ALL + ' '
    #exit( 66)

def printn( s):
    print( s, end='')

pktmon_prefix = ""

def prettify_tcpdump_line_so_it_looks_nice( line):
    global pktmon_prefix
    
    #print( f"{Back.BLACK}{Style.BRIGHT}{Fore.YELLOW}old:{Style.RESET_ALL}{line}")
    if detectlocal:
        """
        : lo: <LOOPBACK,UP,LOWER_UP> mtu 16436 qdisc noqueue
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast qlen 1000
    link/ether 00:50:56:86:e1:46 brd ff:ff:ff:ff:ff:ff
    inet 10.2.2.218/24 brd 10.2.2.255 scope global eth0
    inet6 fe80::250:56ff:fe86:e146/64 scope link
       valid_lft forever preferred_lft forever
3: sit0: <NOARP> mtu 1480 qdisc noop
    link/sit 0.0.0.0 brd 0.0.0.0
"""
        ip_addr_link_local = re.search(r'\slink/\w+\s+([\d\.a-f:]+)\s', line)
        ip_addr_ip_local = re.search(r'\sinet6?\s+([\d\.a-f:]+)\/(\d+)', line)
        ip_addr_link_or_ip_brd = re.search(r'\sbrd\s+([\d\.a-f:]+)\s', line)
        if ip_addr_link_local:
            # print('IP ADDR LINK:', ip_addr_link_local.group(1))
            all_adds.append( ip_addr_link_local.group(1))
        if ip_addr_ip_local:
            # print('IP ADDR IP:', ip_addr_ip_local.group(1))
            all_adds.append( ip_addr_ip_local.group(1))
            # Calculate broadcast just in case, as IPv6 broadcast are not always shown?
            if re.search(':', ip_addr_ip_local.group(1)):
                local_net = ipaddress.IPv6Network( ip_addr_ip_local.group(1) + '/' + ip_addr_ip_local.group(2), False)
            else:
                local_net = ipaddress.IPv4Network( ip_addr_ip_local.group(1) + '/' + ip_addr_ip_local.group(2), False)
            all_adds.append( str(local_net.broadcast_address))
            # print('Broadcast:', local_net.broadcast_address)
        if ip_addr_link_or_ip_brd:
            # print('IP ADDR BRD:', ip_addr_link_or_ip_brd.group(1))
            all_broadcasts.append( ip_addr_link_or_ip_brd.group(1))
        # line = pktmon_udp_pkt.group(1) + pktmon_udp_pkt.group(2) + pktmon_udp_pkt.group(3)

    # Process identification: extract source IP:port and look it up early,
    # before any direction-reversing transformations.
    # Insert [proc:pid] right after the source address (before " > ").
    _src_ip, _src_port = None, None
    if pids_enabled:
        _src_ip, _src_port = _extract_source_addr(line)
        if _src_ip and _src_port:
            _proc = process_map.get((_src_ip, int(_src_port)))
            if _proc:
                _pname, _pid = _proc
                _tag = '[' + crc_colorize(_pname) + crc_colorize(str(_pid)) + ']'
                # IPv4: "IP 10.0.0.5.52341 > ..."
                line = re.sub(
                    '(' + ipv4_addr + r'(\.\d+))\s+>',
                    r'\1' + _tag + r' >',
                    line, count=1
                )
                # IPv6 bracket: "IP6 [2001:db8::1].8080 > ..."
                line = re.sub(
                    r'(\[' + ipv6_addr + r'\](\.\d+))\s+>',
                    r'\1' + _tag + r' >',
                    line, count=1
                )


    """
    CF +QoS DA:E4-A4-71-B3-75-72 BSSID:80-26-89-AB-D9-84 SA:E4-A4-71-B3-75-72 Data IV:3aaaa Pad 0 KeyID 0
    """
    if re.search(r'^\s+CF \+QoS DA', line):
        # Doesn't look too useful
        return


    if re.search( ' IP6? .*?53(:| >) .* (A|AAAA)', line):
        if debug:
          print('found DNS!')
        """
015928.483 IP6 fe80::f405:ed12:ae26:7971.5353 > ff02::fb.5353: 0 A (QM)? wpad.local. (28)
015928.486 IP6 fe80::f405:ed12:ae26:7971.5353 > ff02::fb.5353: 0 AAAA (QM)? wpad.local. (28)
02:28:21.105740 IP 172.30.253.88.53418 > 1.1.1.1.53: 18184+ A? blah.com. (26)
02:28:21.177084 IP 172.30.253.88.40745 > 1.1.1.1.53: 25446+ AAAA? blah.com. (26)
        """
    dns_query = re.search(r'\.(\d+) > (.*?53: \d+).*?\? ([\w\.]+)\.', line)
    if dns_query:
        store_dns_info( dns_query)
        line = re.sub(r'\?\s(.*?)\.\s\(\d+\)', colorize_matches_within, line)


    """
02:33:56.598637 IP 1.1.1.1.53 > 172.30.253.88.40418: 909 1/0/0 A 189.113.174.199 (42)
04:16:50.506404 IP 1.1.1.1.53 > 172.30.253.88.43389: 55004 2/0/0 CNAME HDRedirect-LB7-5a03e1c2772e1c9c.elb.us-east-1.amazonaws.com., A 3.223.115.185 (113)
04:21:35.711426 IP 172.30.240.1.53 > 172.30.253.88.47204: 20303- 5/0/0 CNAME github.github.io., A 185.199.109.153, A 185.199.108.153, A 185.199.110.153, A 185.199.111.153 (158)
04:32:36.555860 IP 172.30.240.1.53 > 172.30.253.88.51003: 5787- 6/0/0 A 74.6.231.21, A 74.6.143.25, A 74.6.231.20, A 98.137.11.164, A 98.137.11.163, A 74.6.143.26 (132)
    """
    dns_response = re.search(r'IP6? (.*?.53) > .*?\.(\d+): (\d+)-? \d+\/\d+\/\d+.*? (?:A|AAAA) ([\w\.:, ]+) \(', line)
    if dns_response:
        match_dns_info(dns_response)

    # See if local addresses / broadcasters can be placed on the left
    for add in all_adds:
        if re.search( rf' > {add}(:|\.{port})', line):
            #print( "LOCAL on the right found")
            line = re.sub( rf'\s({proto})\s(.*) > (.*?):\s', 
                rf' \g<1> {Back.BLACK}{Style.BRIGHT}{Fore.GREEN}>>{Style.RESET_ALL}\g<3> < \g<2>: ', line)
        else:
            # Any local ones are now all on the left already
            line = re.sub( 
                rf'\s({add})(:|\.{port}) > ', 
                rf' {Back.BLACK}{Style.BRIGHT}{Fore.GREEN}>>{Style.RESET_ALL}\g<1>\g<2> > ', line)

    for add in all_broadcasts:
        if re.search( ' > ' + add + rf'(:|\.{port})', line):
            print( "BROADCAST found")
            line = re.sub( rf'^([0-9:\.]+\s{proto})\s({ipv4_addr})(\s|:|\.)', 
                rf' \g<1> {Back.BLACK}{Style.BRIGHT}{Fore.YELLOW}(({Style.RESET_ALL}'
                + rf'\g<2>{Back.BLACK}{Style.BRIGHT}{Fore.YELLOW})){Style.RESET_ALL}'
                + r'\g<3>', line)

    # Time refix reformatting, works for  pktmon & tcpdump
    #line = re.sub( '^(\d{2}):(\d{2}):(\d{2})\.(\d{3})\d+\s', '\g<1>\g<2>\g<3>.\g<4> ', line)
    line = re.sub( r'^(\d{2}):(\d{2}):(\d{2})\.(\d{3})\d+\s', colorize_timestamp, line)

    # pktmon.exe:
    """
    BSSID:80-26-89-AB-D9-84 SA:E4-A4-71-B3-75-72 DA:80-26-89-AB-D9-84 LLC, dsap SNAP (0xaa) Individual, ssap SNAP (0xaa) Command, ctrl 0x03: oui Ethernet (0x000000), ethertype IPv6 (0x86dd), length 99: 2001:e68:542c:361a:2092:bc22:2d56:3032.63292 > 2404:6800:4001:80e::200e.443: Flags [P.], seq 2226039764:2226039803, ack 1995787296, win 513, length 39
    """
    pktmon_logline = re.search(r'PktGroupId \d+, .*? Direction (.x) , Type (.*?) ,', line)
    if pktmon_logline:
        #print('MARK2', pktmon_logline.group(1), pktmon_logline.group(2), 'END' )
        pktmon_prefix = re.sub( ' PktGroupId.*', '', line)
        #print('MARK3', pktmon_prefix)
        # Don't print this line unless we want ARP traffic (rarely)
        return
    elif pktmon_prefix != "":
        line = f"{pktmon_prefix} {line}"

    # TODO: Speed up matching based on source program detected


    if re.search( 'BSSID:.*?, ethertype IP', line):
        printn('WiFiPkt?:')
        line = re.sub( rf'\s+BSSID:.*?, ethertype (IPv\d) .*?: (.*)$', r' \g<1> \g<2>', line)
        line = re.sub( ' (IPv4) ', rf' {Back.BLACK}{Style.BRIGHT}{Fore.GREEN}\g<1>{Style.RESET_ALL} ', line)
        line = re.sub( ' (IPv6) ', rf' {Back.BLACK}{Style.BRIGHT}{Fore.CYAN}\g<1>{Style.RESET_ALL} ', line)
        line = re.sub( rf'({ipv4_addr})\.({port})', colorize_match_ip_port, line)
        line = re.sub( rf'({ipv6_addr})\.({port})', colorize_match_ip6_port, line)
        line = re.sub( rf'seq (\d+):(\d+),', colorize_matches_within, line)
        line = re.sub( rf'ack (\d+),', colorize_matches_within, line)

    """
00-0C-29-07-BD-09 > FF-FF-FF-FF-FF-FF, ethertype IPv4 (0x0800), length 342: 0.0.0.0.68 > 255.255.255.255.67: UDP, length 300
    """
    pktmon_udp_pkt = re.search(r'^([\d\.]+)\s+[0-9A-F]{2}-[0-9A-F]{2}.*?, ethertype (IPv\d) .*?: (.*: UDP, length \d+)$', line)
    if pktmon_udp_pkt:
        printn('UDP:')
        line = pktmon_udp_pkt.group(1) + pktmon_udp_pkt.group(2) + pktmon_udp_pkt.group(3)
        #line = re.sub('[0-9A-F]{2}-[0-9A-F]{2}.*?, ethertype (IPv\d) .*?: (.*: UDP, length \d+)$', '\g<1> \g<2>', line)

    """
00-15-5D-A4-2F-20 > 00-15-5D-0F-F3-BA, ethertype IPv4 (0x0800), length 67: 172.30.240.1.60169 > 172.30.253.88.45885: Flags [P.], seq 1151420986:1151420999, ack 1349378398, win 8211, length 13
00-15-5D-A4-2F-20 > 00-15-5D-0F-F3-BA, ethertype IPv4 (0x0800), length 67: 172.30.240.1.50118 > 172.30.253.88.45885: Flags [P.], seq 831973636:831973649, ack 150871422, win 8209, length 13
130704.020      00-15-5D-A4-2F-20 > 00-15-5D-0F-F3-BA, ethertype IPv4 (0x0800), length 67: 172.30.240.1.60169 > 172.30.253.88.45885: Flags [P.], seq 1151420986:1151420999, ack 1349378398, win 8211, length 13
    """
    pktmon_tcp_pkt = re.search(r'([\d\.]+)\s+[0-9A-F]{2}-[0-9A-F]{2}.*?, ethertype (IPv\d) .*?:( .*?Flags.*)$', line)
    if pktmon_tcp_pkt:
        printn('TCP:')
        line = pktmon_tcp_pkt.group(1) + ' ' + pktmon_tcp_pkt.group(2) + pktmon_tcp_pkt.group(3)
        line = re.sub( ' (IPv4) ', rf' {Back.BLACK}{Style.BRIGHT}{Fore.GREEN}\g<1>{Style.RESET_ALL} ', line)
        line = re.sub( ' (IPv6) ', rf' {Back.BLACK}{Style.BRIGHT}{Fore.CYAN}\g<1>{Style.RESET_ALL} ', line)
        line = re.sub( rf'seq (\d+):(\d+),', colorize_matches_within, line)
        line = re.sub( rf'ack (\d+),', colorize_matches_within, line)
        #line = re.sub('[0-9A-F]{2}-[0-9A-F]{2}.*?, ethertype (IPv\d) .*?: (.*: Flags .*  length \d+)$', '\g<1> \g<2>', line)

    if re.search( ' IP .*: (?:tcp |UDP,|Flags)', line):
        line = re.sub( rf'({ipv4_addr})\.({port})', colorize_match_ip_port, line)
    elif re.search( ' IP6 .*: (?:tcp |UDP,|Flags|0)', line):
        line = re.sub( rf'({ipv6_addr})\.({port})', colorize_match_ip6_port, line)
    # Traceroute detection and annotation
    if re.search( r'^\s*traceroute', line):
        # Header line: 'traceroute to host (IP), hops max, packets'
        def colorize_traceroute_header_ip(m):
            # Re-wrap the match object so group(1) is the IP
            class FakeMatch:
                def __init__(self, ip):
                    self._ip = ip
                def group(self, n):
                    return self._ip
            return m.group(1) + colorize_match_ip(FakeMatch(m.group(2)))
        line = re.sub(
            rf'(traceroute to \S+ )\(?({ipv4_addr})\)?',
            colorize_traceroute_header_ip,
            line
        )
    elif re.search( r'^\s*\d+\s+\S+\s*\(', line):
        # Hop line: ' N  HOSTNAME (IP)  TIME ms' or ' N  IP (IP)  TIME ms'
        def colorize_traceroute_hop_ip(m):
            class FakeMatch:
                def __init__(self, ip):
                    self._ip = ip
                def group(self, n):
                    return self._ip
            # m.group(1) = hop number + whitespace + hostname
            # m.group(2) = opening paren
            # m.group(3) = IP
            # m.group(4) = closing paren + whitespace
            return m.group(1) + m.group(2) + colorize_match_ip(FakeMatch(m.group(3))) + m.group(4)
        line = re.sub(
            rf'(\d+\s+\S+\s*)(\()?({ipv4_addr})(\)?)',
            colorize_traceroute_hop_ip,
            line
        )
    elif re.search( ': ICMP ', line):
        line = re.sub( f'({ipv4_addr})', colorize_match_ip, line)
        line = re.sub( '(ICMP echo request)', rf'{Back.BLACK}{Fore.GREEN}\g<1>{Style.RESET_ALL}', line)
        line = re.sub( '(ICMP echo reply)', rf'{Back.BLACK}{Style.BRIGHT}{Fore.GREEN}\g<1>{Style.RESET_ALL}', line)

    elif re.search( ': ICMP6', line):
        # Bare IPv6 addresses: anchor to 'IP6 ' / '> ' so timestamps
        # ('15:52:21' also looks like hex-colons!) don't get colorized.
        # Greedy hex/colon run (must end on a hex digit) - the ipv6_addr
        # regex alone stops at the shortest alternative ('fe80::').
        line = re.sub( r'(?<=[6>] )([0-9a-fA-F:]+[0-9a-fA-F](?:%[0-9a-zA-Z]+)?)', colorize_match_ip6, line)
    elif re.search( ' ARP', line):
        # ARP, Request who-has 172.30.253.88 (00:15:5d:0f:f3:ba) tell 172.30.240.1, length 28
        line = re.sub( ', Request who-has (.*?) tell (.*?),', 
                 f' {Back.BLACK}{Style.BRIGHT}{Fore.YELLOW}(({Style.RESET_ALL}'
                + rf'\g<2>{Back.BLACK}{Style.BRIGHT}{Fore.YELLOW})){Style.RESET_ALL}'
                + rf' who-has \g<1>'
            , line)
        # ARP, Reply 172.30.253.88 is-at 00:15:5d:0f:f3:ba, length 28
        # Color ARP reply similarly to ICMP reply (bright green on black bg)
        arp_reply_style = Back.BLACK + Style.BRIGHT + Fore.GREEN
        line = re.sub( rf', Reply ({ipv4_addr}) is-at (.*?),',
                 rf' {arp_reply_style}(\1{arp_reply_style}){Style.RESET_ALL} reply: \2', line)
    else:
        line = re.sub( f'({ipv4_addr})', colorize_match, line)

    # Deal with all 'Flags [...]' in one place (also drops the word 'Flags' for terseness)
    line = re.sub( r'(Flags )(\[[SFPURWE.]+\])', colorize_flags, line)

    # IPv6 family colour (cyan keyword, everywhere) + L2 control-plane
    # protocols (STP, CDP, UDLD, LLDP, ...) in magenta
    line = re.sub( r'\b(IP6)\b', IP6_STYLE + r'\g<1>' + Style.RESET_ALL, line)
    line = re.sub( rf'\b({L2_CONTROL_KEYWORDS})\b', L2_STYLE + r'\g<1>' + Style.RESET_ALL, line)

    # TODO: Other things to learn and figure out:
    """
15:52:18.765035 IP6 fe80::4896:8753:a9ba:662e > fe80::250:56ff:feaa:3c0c: ICMP6, neighbor solicitation, who has fe80::250:56ff:feaa:3c0c, length 32
15:52:18.765097 IP6 fe80::250:56ff:feaa:3c0c > fe80::4896:8753:a9ba:662e: ICMP6, neighbor advertisement, tgt is fe80::250:56ff:feaa:3c0c, length 24
15:52:18.772045 IP6 fe80::250:56ff:feaa:3c0c > fe80::4896:8753:a9ba:662e: ICMP6, neighbor solicitation, who has fe80::4896:8753:a9ba:662e, length 32
15:52:18.772556 IP6 fe80::4896:8753:a9ba:662e > fe80::250:56ff:feaa:3c0c: ICMP6, neighbor advertisement, tgt is fe80::4896:8753:a9ba:662e, length 32
    """

    line = re.sub( ' > ', Back.BLACK + Style.BRIGHT + Fore.RED  + ' > ' + Style.RESET_ALL, line)
    line = re.sub( ' < ', Back.BLACK + Style.BRIGHT + Fore.BLUE + ' < ' + Style.RESET_ALL, line)
    #print( "nice: ", line)

    if args.wrap:
        print( line)
    else:
        terminal_size = os.get_terminal_size()
        # Print the size
        # of the terminal
        linesize_without_ansi = len( ansi_escape.sub('', line))
        if terminal_size.columns < linesize_without_ansi:
            # print('CUT')
            # Assume there's no ansi sequences in the latter part of the string
            # yes this may be a gamble but usually it should work
            cut_line = line[:-(linesize_without_ansi - terminal_size.columns +1 )] + '>'
            print( cut_line)
        else:
            print( line)

# regex below adapted from incomplete answer that doesn't address 24bit colors here:
# https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python
# colored text: 155740.
# repr() of the above: '\x01\x1b[38;2;0;250;255m\x02\x01\x1b[48;2;0;0;0m\x0215\x01\x1b[38;2;124;0;255m\x02\x01\x1b[48;2;0;0;0m\x0257\x01\x1b[38;2;0;220;255m\x02\x01\x1b[48;2;0;0;0m\x0240\x1b[0m.
# @-Z = @ plus capitals. 0-? is numbers plus :;<=>?. @-~ is cap and nocapletters plus {}|~
ansi_escape = re.compile(r'(\x01)?\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])[\x01\x02]*')

if args.info:
    ip = args.info[0]
    print( get_ip_info( ip).lstrip())
    exit(0)

if args.read == '-':
    if debug:
      print( 'CTD: Reading from stdin ...' )
    for line in sys.stdin:
        prettify_tcpdump_line_so_it_looks_nice( line.rstrip())
    exit(0)
else:
  # Assume it's a file?
  pass

exit(1)
