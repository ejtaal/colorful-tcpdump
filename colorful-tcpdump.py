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
Back.BLUE + Fore.MAGENTA,
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
Back.YELLOW + Fore.MAGENTA,
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
proto = '[A-Z]{1,8}' # is 8 enough?
#ipv6_rev = qr/(?:(?:$hex\.){31}$hex)/;
#ipv6_addr = qr/(?:$ipv6_addr|$ipv6_rev)/;



def colorize_match( matchobj):
    return crc_colorize( matchobj.group(0))

def prettify_tcpdump_line_so_it_looks_nice( line):
    #print( "old:  ", line)
    for add in all_adds:
        if re.search( ' > ' + add + '.' + port, line):
            #print( "LOCAL on the right found")
            line = re.sub( '\s('+proto+')\s(.*) > (.*?):\s', ' \g<1> \g<3> < \g<2>: ', line)

    line = re.sub( ipv4_addr, colorize_match, line)
    line = re.sub( ' > ', Back.BLACK + Style.BRIGHT + Fore.RED + ' -> ' + Style.RESET_ALL, line)
    line = re.sub( ' < ', Back.BLACK + Style.BRIGHT + Fore.BLUE + ' <- ' + Style.RESET_ALL, line)
    print( "nice: ", line)
    

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
print(out)
print(err)

