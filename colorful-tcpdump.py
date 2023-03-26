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
usage_text_full = """

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

### Set up everything to do with colours. Some of the basic color stuff is no longer used, TODO: remove that
from typing import Iterable, Tuple
import colorsys
import itertools
from fractions import Fraction
from pprint import pprint

def zenos_dichotomy() -> Iterable[Fraction]:
    """
    http://en.wikipedia.org/wiki/1/2_%2B_1/4_%2B_1/8_%2B_1/16_%2B_%C2%B7_%C2%B7_%C2%B7
    """
    for k in itertools.count():
        yield Fraction(1,2**k)

def fracs() -> Iterable[Fraction]:
    """
    [Fraction(0, 1), Fraction(1, 2), Fraction(1, 4), Fraction(3, 4), Fraction(1, 8), Fraction(3, 8), Fraction(5, 8), Fraction(7, 8), Fraction(1, 16), Fraction(3, 16), ...]
    [0.0, 0.5, 0.25, 0.75, 0.125, 0.375, 0.625, 0.875, 0.0625, 0.1875, ...]
    """
    yield Fraction(0)
    for k in zenos_dichotomy():
        i = k.denominator # [1,2,4,8,16,...]
        for j in range(1,i,2):
            yield Fraction(j,i)

# can be used for the v in hsv to map linear values 0..1 to something that looks equidistant
# bias = lambda x: (math.sqrt(x/3)/Fraction(2,3)+Fraction(1,3))/Fraction(6,5)

HSVTuple = Tuple[Fraction, Fraction, Fraction]
RGBTuple = Tuple[float, float, float]

def hue_to_tones(h: Fraction) -> Iterable[HSVTuple]:
    for s in [Fraction(6,10)]: # optionally use range
        #for v in [Fraction(8,10),Fraction(5,10)]: # could use range too
        for v in [Fraction(8,10),Fraction(7,10)]: # could use range too
            yield (h, s, v) # use bias for v here if you use range

def hsv_to_rgb(x: HSVTuple) -> RGBTuple:
    return colorsys.hsv_to_rgb(*map(float, x))

flatten = itertools.chain.from_iterable

def hsvs() -> Iterable[HSVTuple]:
    return flatten(map(hue_to_tones, fracs()))

def rgbs() -> Iterable[RGBTuple]:
    return map(hsv_to_rgb, hsvs())

def rgb_to_css(x: RGBTuple) -> str:
    #uint8tuple = map(lambda y: int(y*255), x)
    t = tuple(map(lambda y: int(y*255), x))
    tup = list(t) + [0]
    #:w
    # tup[3] = 0
    if (0.299 * tup[0] + 0.587 * tup[1] + 0.114 * tup[2])/255 > 0.5:
        tup[3] = 1
    
    return tup
    #return "rgb({},{},{})".format(*uint8tuple)

def css_colors() -> Iterable[str]:
    return map(rgb_to_css, rgbs())

def rainbowColor( percent_x2):
    # Based on: https://github.com/gnachman/iTerm2/blob/master/tests/24-bit-color.sh
    h = int(percent_x2 / 43)
    f = int(percent_x2 - 43 * h)
    t = int(f * 255 / 43)
    q = 255 - t
    if h == 0:
        rgb = ( 255, t, 0)
    if h == 1:
        rgb = ( q, 255, 0)
    if h == 2:
        rgb = ( 0, 255, t)
    if h == 3:
        rgb = ( 0, q, 255)
    if h == 4:
        rgb = ( t, 0, 255)
    if h == 5:
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
nice_colors = [
#Back.BLUE + Fore.GREEN,
Back.BLUE + Fore.YELLOW,
#Back.BLUE + Fore.MAGENTA,
Back.BLUE + Fore.CYAN,
Back.BLUE + Fore.WHITE,
Back.BLUE + Style.BRIGHT + Fore.RED,
Back.BLUE + Style.BRIGHT + Fore.GREEN,
Back.BLUE + Style.BRIGHT + Fore.YELLOW,
Back.BLUE + Style.BRIGHT + Fore.BLUE,
#Back.BLUE + Style.BRIGHT + Fore.MAGENTA,
Back.BLUE + Style.BRIGHT + Fore.CYAN,
Back.BLUE + Style.BRIGHT + Fore.WHITE,

Back.WHITE + Fore.RED,
#Back.WHITE + Fore.YELLOW,
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

#Back.RED + Fore.GREEN,
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
#Back.BLACK + Style.BRIGHT + Fore.WHITE,
]
nice_colors_num = len( nice_colors)

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

# RGB values of:
#  1 00X
#  2 0X0
#  3 0XX
#  4 X00
#  5 X0X
#  6 XX0
#  7 XXX
#s of 95, 0, 0

nice_colors = []
color24b_step = 20
color24b_min_intensity = 150
color24b_gradients = int( 1 + (255 - color24b_min_intensity) / color24b_step)
color24b_total = \
    3 * color24b_gradients + \
    3 * color24b_gradients ** 2 + \
        color24b_gradients ** 3

color24b_rgb_steps = [0]
color24b_rgb_steps += list( range( 255, 255 - color24b_step * color24b_gradients - 1, -color24b_step))
#print( *range( 255, 255 - color24b_step * #color24b_gradients, color24b_step))
for r in color24b_rgb_steps:
    for g in color24b_rgb_steps:
        for b in color24b_rgb_steps:
            if not (r == 0 and r == g and g == b):
                # If these are taken as background, then calc a suitable foreground:
                f=1
                nice_colors += [( r, g, b, f)]
                nice_colors += [( r, g, b, 2)]
                #print( f'rgb: {r},{g},{b}')


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

#for i in nice_colors:
#    print( i + "Some text that is supposed to be readable" + Style.RESET_ALL)
#print(Style.RESET_ALL)
#print('back to normal now')

#for c in sample_colors:
#    print( rgb_ansi( c) + "Some text that is supposed to be readable")

def usage():
    colored_logo = ctd_logo
    colored_logo = re.sub( '([^\s]{1,6})', r, colored_logo)

    colored_logo = re.sub( '([^\s]{1,6})', colorize_match, colored_logo)
    #colored_logo = re.sub( '(_+)', Fore.BLUE + '\g<1>' + Style.RESET_ALL, colored_logo)
    #colored_logo = re.sub( '_/', f'_{Style.BRIGHT}{Fore.BLUE}/{Style.RESET_ALL}', colored_logo)

    print( colored_logo)

#    print(cmd)
    global cmd
    print( cmd)
    if len( cmd) > 1 and cmd[1] == '--help':
        print("MARK")
        print( usage_text_full)
    else:
        print( usage_text_short)
    exit(1)

import argparse
#parser = argparse.ArgumentParser( description='A script to prettify tcpdump output and increase information about IPs & networks', usage=usage())
parser = argparse.ArgumentParser( description='A script to prettify tcpdump output and tersely display just a bit more information about the IPs & networks that are seen')
parser.add_argument( '--debug', action='store_true')
parser.add_argument( '-d', action='store_true')
parser.add_argument( '--detect-local-from-input', action='store_true')
parser.add_argument( '--nocolor', action='store_false')
# Note! dashes are converted into underscores else it's not valid python! So it becomes args.myip_override
parser.add_argument( '--myip-override', metavar='MYIP_OVERRIDE', type=str, nargs='?')

group = parser.add_mutually_exclusive_group( required=True)
group.add_argument( '--info', metavar='IP', type=str, nargs='?')
group.add_argument( 'read', metavar='FILE_TO_READ',  type=str, nargs='?')

args = parser.parse_args()

if args.debug:
  debug = True

if args.nocolor is False:
  nocolor = True

if args.d or args.detect_local_from_input:
    detectlocal = True
### Get local interface addresses

all_adds = []
all_broadcasts = []
all_ifs = []


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
            all_ifs.append( value)
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
      print( crc_colorize( a))

  print( 'Local broadcast addresses:')
  for b in all_broadcasts:
      print( crc_colorize( b))


import re

import time
import queue
import sys
import threading
import subprocess
PIPE = subprocess.PIPE

if debug:
  print("Argument List:", str(sys.argv))

#cmd = ['/sbin/tcpdump', '-qlni', 'eth0']
#cmd = ['/sbin/tcpdump', '-lni', 'eth0']

# TODO: add check for windows / windump / tshark?
# TODO: Rather, detect it based on input
# TODO: Parse those arguments so nicely described in the usage notes
# cmd = ['/sbin/tcpdump']
# cmd += sys.argv[1:]
cmd = sys.argv



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
ipv6_grp = f'{hexre}{1,4}';
ipv6_addr = f'(?:::)?(?:{ipv6_grp}::?)+{ipv6_grp}(?:::)?'
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

# Opening JSON file
if debug:
  print("Loading range data...")
with open('data/ctd-data.json') as json_file:
    data = json.load(json_file)
    for key,value in data.items():
        if debug:
          print( key + ' ', end='')
        ranges_info[ key] = data[ key]
    #pprint( ranges_info)
if debug:
  print('')
  print("Done")

import ipaddress

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

        if 'subdivisions' in geoip:
            info += '/' + crc_colorize(geoip['subdivisions'][0]['iso_code'])

    if info != "":
        info = f'[{info}]'

    for descr in ranges_info.keys():
        moreinfo = []
        return_info = ""
        #print( 'descr: ', descr)
        for tup in ranges_info[ descr]:
            r = tup[0]
            rinfo = tup[1]
            #pprint( r)
            found=False
            if ':' not in ip and ':' not in r:
                if ipaddress.IPv4Address( ip) in ipaddress.IPv4Network(r):
                    found=True
                    #print( 'Found ', ip, ' in range ', r, ' which is ', crc_colorize( rinfo))
            elif ':' in ip and ':' in r:
                if ipaddress.IPv6Address( ip) in ipaddress.IPv6Network(r):
                    found=True
#            if ip.search('\.') and ipaddress.IPv4Address( ip) in ipaddress.IPv4Network(r)
#            or ipaddress.IPv6Address( ip) in ipaddress.IPv6Network(r):
                #print( 'ip is in net', ip, r)
            if found:
                moreinfo += [rinfo]

        #print( 'moreinfo: ', moreinfo)
        if len(moreinfo) > 0:
            addinfo = crc_colorize( descr)
            seen = []
            for i in moreinfo:
                #print( 'i: ', i)
                #print( 'seen: ', seen)
                #if i in seen:
                #    print('i in seen?')
                #else:
                #    print('i NOT in seen?')
                if i not in seen and i != "":
                    addinfo += '/' + crc_colorize( i)
                    #print( 'addinfo: ', addinfo)
                seen += [i]
            info += f'[{addinfo}]'

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
    print("MARK")
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

def colorize_match( matchobj):
    return crc_colorize( matchobj.group(1))

def colorize_matches_within( matchobj):
    s = matchobj.group(0)
    #print('IN MATCHES')
    for m in matchobj.groups():
        s = s.replace( m, crc_colorize( m))
    
    return s

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
    detectlocal = False
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
        ip_addr_link_local = re.search('\slink/\w+\s+([\d\.a-f:]+)\s', line)
        ip_addr_ip_local = re.search('\sinet6?\s+([\d\.a-f:]+)\/(\d+)', line)
        ip_addr_link_or_ip_brd = re.search('\sbrd\s+([\d\.a-f:]+)\s', line)
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


    """
    CF +QoS DA:E4-A4-71-B3-75-72 BSSID:80-26-89-AB-D9-84 SA:E4-A4-71-B3-75-72 Data IV:3aaaa Pad 0 KeyID 0
    """
    if re.search('^\s+CF \+QoS DA', line):
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
    dns_query = re.search( '\.(\d+) > (.*?53: \d+).*?\? ([\w\.]+)\.', line)
    if dns_query:
        store_dns_info( dns_query)

    """
02:33:56.598637 IP 1.1.1.1.53 > 172.30.253.88.40418: 909 1/0/0 A 189.113.174.199 (42)
04:16:50.506404 IP 1.1.1.1.53 > 172.30.253.88.43389: 55004 2/0/0 CNAME HDRedirect-LB7-5a03e1c2772e1c9c.elb.us-east-1.amazonaws.com., A 3.223.115.185 (113)
04:21:35.711426 IP 172.30.240.1.53 > 172.30.253.88.47204: 20303- 5/0/0 CNAME github.github.io., A 185.199.109.153, A 185.199.108.153, A 185.199.110.153, A 185.199.111.153 (158)
04:32:36.555860 IP 172.30.240.1.53 > 172.30.253.88.51003: 5787- 6/0/0 A 74.6.231.21, A 74.6.143.25, A 74.6.231.20, A 98.137.11.164, A 98.137.11.163, A 74.6.143.26 (132)
    """
    dns_response = re.search( 'IP6? (.*?.53) > .*?\.(\d+): (\d+)-? \d+\/\d+\/\d+.*? (?:A|AAAA) ([\w\.:, ]+) \(', line)
    if dns_response:
        match_dns_info(dns_response)

    # See if local addresses / broadcasters can be placed on the left
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

    # Time refix reformatting, works for  pktmon & tcpdump
    #line = re.sub( '^(\d{2}):(\d{2}):(\d{2})\.(\d{3})\d+\s', '\g<1>\g<2>\g<3>.\g<4> ', line)
    line = re.sub( '^(\d{2}):(\d{2}):(\d{2})\.(\d{3})\d+\s', colorize_timestamp, line)

    # pktmon.exe:
    """
    BSSID:80-26-89-AB-D9-84 SA:E4-A4-71-B3-75-72 DA:80-26-89-AB-D9-84 LLC, dsap SNAP (0xaa) Individual, ssap SNAP (0xaa) Command, ctrl 0x03: oui Ethernet (0x000000), ethertype IPv6 (0x86dd), length 99: 2001:e68:542c:361a:2092:bc22:2d56:3032.63292 > 2404:6800:4001:80e::200e.443: Flags [P.], seq 2226039764:2226039803, ack 1995787296, win 513, length 39
    """
    pktmon_logline = re.search( 'PktGroupId \d+, .*? Direction (.x) , Type (.*?) ,', line)
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
        line = re.sub( f'\s+BSSID:.*?, ethertype (IPv\d) .*?: (.*)$', ' \g<1> \g<2>', line)
        line = re.sub( ' (IPv4) ', f' {Back.BLACK}{Style.BRIGHT}{Fore.GREEN}\g<1>{Style.RESET_ALL} ', line)
        line = re.sub( ' (IPv6) ', f' {Back.BLACK}{Style.BRIGHT}{Fore.YELLOW}\g<1>{Style.RESET_ALL} ', line)
        line = re.sub( f'({ipv4_addr})\.({port})', colorize_match_ip_port, line)
        line = re.sub( f'({ipv6_addr})\.({port})', colorize_match_ip_port, line)
        line = re.sub( f'seq (\d+):(\d+),', colorize_matches_within, line)
        line = re.sub( f'ack (\d+),', colorize_matches_within, line)
        line = re.sub( '(Flags )(\[R\])', f'\g<1>{Back.RED}{Fore.WHITE}\g<2>{Style.RESET_ALL}', line)
        line = re.sub( '(Flags )(\[S\])', f'\g<1>{Back.BLACK}{Fore.GREEN}\g<2>{Style.RESET_ALL}', line)
        line = re.sub( '(Flags )(\[S\.\])', f'\g<1>{Back.BLACK}{Style.BRIGHT}{Fore.GREEN}\g<2>{Style.RESET_ALL}', line)
        line = re.sub( '(Flags )(\[P.\])', f'\g<1>{Back.GREEN}{Fore.WHITE}\g<2>{Style.RESET_ALL}', line)
        line = re.sub( '(Flags )(\[\.\])', f'\g<1>{Back.GREEN}{Style.BRIGHT}{Fore.WHITE}\g<2>{Style.RESET_ALL}', line)

    """
00-0C-29-07-BD-09 > FF-FF-FF-FF-FF-FF, ethertype IPv4 (0x0800), length 342: 0.0.0.0.68 > 255.255.255.255.67: UDP, length 300
    """
    pktmon_udp_pkt = re.search('^([\d\.]+)\s+[0-9A-F]{2}-[0-9A-F]{2}.*?, ethertype (IPv\d) .*?: (.*: UDP, length \d+)$', line)
    if pktmon_udp_pkt:
        printn('UDP:')
        line = pktmon_udp_pkt.group(1) + pktmon_udp_pkt.group(2) + pktmon_udp_pkt.group(3)
        #line = re.sub('[0-9A-F]{2}-[0-9A-F]{2}.*?, ethertype (IPv\d) .*?: (.*: UDP, length \d+)$', '\g<1> \g<2>', line)

    """
00-15-5D-A4-2F-20 > 00-15-5D-0F-F3-BA, ethertype IPv4 (0x0800), length 67: 172.30.240.1.60169 > 172.30.253.88.45885: Flags [P.], seq 1151420986:1151420999, ack 1349378398, win 8211, length 13
00-15-5D-A4-2F-20 > 00-15-5D-0F-F3-BA, ethertype IPv4 (0x0800), length 67: 172.30.240.1.50118 > 172.30.253.88.45885: Flags [P.], seq 831973636:831973649, ack 150871422, win 8209, length 13
130704.020      00-15-5D-A4-2F-20 > 00-15-5D-0F-F3-BA, ethertype IPv4 (0x0800), length 67: 172.30.240.1.60169 > 172.30.253.88.45885: Flags [P.], seq 1151420986:1151420999, ack 1349378398, win 8211, length 13
    """
    pktmon_tcp_pkt = re.search('([\d\.]+)\s+[0-9A-F]{2}-[0-9A-F]{2}.*?, ethertype (IPv\d) .*?:( .*?Flags.*)$', line)
    if pktmon_tcp_pkt:
        printn('TCP:')
        line = pktmon_tcp_pkt.group(1) + ' ' + pktmon_tcp_pkt.group(2) + pktmon_tcp_pkt.group(3)
        line = re.sub( ' (IPv4) ', f' {Back.BLACK}{Style.BRIGHT}{Fore.GREEN}\g<1>{Style.RESET_ALL} ', line)
        line = re.sub( ' (IPv6) ', f' {Back.BLACK}{Style.BRIGHT}{Fore.YELLOW}\g<1>{Style.RESET_ALL} ', line)
        line = re.sub( f'seq (\d+):(\d+),', colorize_matches_within, line)
        line = re.sub( f'ack (\d+),', colorize_matches_within, line)
        line = re.sub( '(Flags )(\[R\])', f'\g<1>{Back.RED}{Fore.WHITE}\g<2>{Style.RESET_ALL}', line)
        line = re.sub( '(Flags )(\[S\])', f'\g<1>{Back.BLACK}{Fore.GREEN}\g<2>{Style.RESET_ALL}', line)
        line = re.sub( '(Flags )(\[S\.\])', f'\g<1>{Back.BLACK}{Style.BRIGHT}{Fore.GREEN}\g<2>{Style.RESET_ALL}', line)
        line = re.sub( '(Flags )(\[P.\])', f'\g<1>{Back.GREEN}{Fore.WHITE}\g<2>{Style.RESET_ALL}', line)
        line = re.sub( '(Flags )(\[\.\])', f'\g<1>{Back.GREEN}{Style.BRIGHT}{Fore.WHITE}\g<2>{Style.RESET_ALL}', line)
        #line = re.sub('[0-9A-F]{2}-[0-9A-F]{2}.*?, ethertype (IPv\d) .*?: (.*: Flags .*  length \d+)$', '\g<1> \g<2>', line)

    if re.search( ' IP .*: (?:tcp |UDP,|Flags)', line):
        line = re.sub( f'({ipv4_addr})\.({port})', colorize_match_ip_port, line)
        line = re.sub( '(Flags )(\[R\])', f'\g<1>{Back.RED}{Fore.WHITE}\g<2>{Style.RESET_ALL}', line)
        line = re.sub( '(Flags )(\[S\])', f'\g<1>{Back.BLACK}{Fore.GREEN}\g<2>{Style.RESET_ALL}', line)
        line = re.sub( '(Flags )(\[S\.\])', f'\g<1>{Back.BLACK}{Style.BRIGHT}{Fore.GREEN}\g<2>{Style.RESET_ALL}', line)
        line = re.sub( '(Flags )(\[P.\])', f'\g<1>{Back.GREEN}{Fore.WHITE}\g<2>{Style.RESET_ALL}', line)
        line = re.sub( '(Flags )(\[\.\])', f'\g<1>{Back.GREEN}{Style.BRIGHT}{Fore.WHITE}\g<2>{Style.RESET_ALL}', line)
    elif re.search( ' IP6 .*: (?:tcp |UDP,|0)', line):
        line = re.sub( f'({ipv6_addr})\.({port})', colorize_match_ip_port, line)
    elif re.search( ': ICMP ', line):
        line = re.sub( f'({ipv4_addr})', colorize_match_ip, line)
        line = re.sub( '(ICMP echo request)', f'{Back.BLACK}{Fore.GREEN}\g<1>{Style.RESET_ALL}', line)
        line = re.sub( '(ICMP echo reply)', f'{Back.BLACK}{Style.BRIGHT}{Fore.GREEN}\g<1>{Style.RESET_ALL}', line)

    # TODO: Check for 'Flags' and deal with them all in one place

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

"""
#### main() ###
"""

import random
### Replace different strings of length 1, 2 .., with the following words:
tcpdump_logo_strings = [ [], ['>', '+', '.', ':', '<'],
    ['::', 'A?', 'IP', 'CF', 'US', 'UK', 'AU', 'IE', 'NZ', 'NL', 'DE', 'FR', 'CA', 'CN', 'RU'],
    ['dns', 'ssh', 'AWS', 'UDP', 'tcp', 'IP6', 'TOR'],
    ['12'+random.choice('123456789')+'.', '23'+random.choice('123456789')+'.', '[S.]', 'MSFT', 'AAAA'],
    [ random.choice('abcdef')+'.com', random.choice('abcdef')+'.net', 'MCAST', 'AZURE', 'LLMNR'],
    ['200'+random.choice('1234567890abcdef')+'::', random.choice('1234567890abcdef')+'f::fb', 'AKAMAI', 'GOOGLE', 'GCLOUD', 'AMAZON'],
    ['RFC1918', '',''],
    ['', '',''],
    ['', '',''],
    ['', '',''],
    ['', '',''],
]

def r( o):
    return random.choice( tcpdump_logo_strings[ len( o.group(0))])



##### Nice RGB color generation algos, taken from:
### https://stackoverflow.com/questions/470690/how-to-automatically-generate-n-distinct-colors


if args.info:
    if debug:
      print( f'Lookup info about {args.info} ...' )
    print( get_ip_info( args.info).lstrip())
    exit(0)

if debug:
  print( 'read = ', args.read)

if args.read == '-':
    #print( 'CTD: Reading from stdin ...' )
    for line in sys.stdin:
        #print( f'line: {line.rstrip()}')
        prettify_tcpdump_line_so_it_looks_nice( line.rstrip())
    exit(0)
else:
  # Assume it's a file?
  pass

exit(1)


#if len( cmd) == 2 and cmd[1] == '-':
#    print( 'CTD: Reading from stdin ...' )
#    for line in sys.stdin:
#        #print( f'line: {line.rstrip()}')
#        prettify_tcpdump_line_so_it_looks_nice( line.rstrip())
#    exit(0)
#
#if len( cmd) > 1 and cmd[1] == '--info':
#    print( f'Lookup info about {cmd[2]} ...' )
#    print( get_ip_info( cmd[2]))
#    exit(0)
#
#if len

#if len( cmd) < 2 or cmd[1] == '-h' or cmd[1] == '--help':
# Something didn't go quite right?
usage()

exit(0)
