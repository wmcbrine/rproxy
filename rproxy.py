#!/usr/bin/env python

# Remote Proxy for TiVo, v0.2
# Copyright 2014 William McBrine
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You didn't receive a copy of the license with this program because 
# you already have dozens of copies, don't you? If not, visit gnu.org.

""" Remote Proxy for TiVo

    This is a server that connects to the "Crestron" interface on a
    Series 3 or later TiVo, and reflects the port back out, allowing
    multiple simultaneous connections. (The TiVo allows only one.)
    Commands are queued from all sources, and sent to the TiVo no more
    often than once every tenth of a second, avoiding overload. Status
    responses are sent back to all connected clients. In other words, it
    works like the spec says the TiVo service is supposed to. :)

    Takes the address of the TiVo to connect to as the only parameter.

"""

__author__ = 'William McBrine <wmcbrine@gmail.com>'
__version__ = '0.2'
__license__ = 'GPL'

import getopt
import socket
import sys
import thread
import time

TIVO_REMOTE_PORT1 = 31339

in_process = False
queue = []
listeners = []
tivo = None
verbose = False

def process_queue():
    global in_process
    while in_process:
        if queue:
            msg = queue.pop(0)
            if verbose:
                sys.stderr.write('%s\n' % msg)
            try:
                tivo.sendall(msg)
            except:
                break
            time.sleep(0.1)
        else:
            time.sleep(0.02)
    in_process = False

def read_client(client):
    global in_process
    while True:
        try:
            msg = client.recv(1024)
        except:
            break
        if not msg:
            break
        queue.append(msg)
        if not in_process:
            in_process = True
            thread.start_new_thread(process_queue, ())
    try:
        client.close()
    except:
        pass

def status_update():
    global tivo, listeners
    while True:
        try:
            status = tivo.recv(1024)
        except:
            status = ''
        if not status:
            try:
                tivo.close()
            except:
                pass
            tivo = None
            break
        if verbose:
            sys.stderr.write('%s\n' % status)
        for l in listeners[:]:
            try:
                l.sendall(status)
            except:
                listeners.remove(l)

def connect(target):
    global tivo
    try:
        tivo = socket.socket()
        tivo.settimeout(5)
        tivo.connect(target)
        tivo.settimeout(None)
    except:
        raise

if len(sys.argv) < 2:
    sys.stderr.write('Must specify an address\n')
    sys.exit(1)

try:
    opts, t_address = getopt.getopt(sys.argv[1:], 'v', ['verbose'])
except getopt.GetoptError, msg:
    sys.stderr.write('%s\n' % msg)

for opt, value in opts:
    if opt in ('-v', '--verbose'):
        verbose = True

t_address = t_address[0]
if ':' in t_address:
    t_address, t_port = address.split(':')
    t_port = int(t_port)
else:
    t_port = TIVO_REMOTE_PORT1
connect((t_address, t_port))

thread.start_new_thread(status_update, ())

server = socket.socket()
server.bind(('', TIVO_REMOTE_PORT1))
server.listen(5)

try:
    while True:
        client, address = server.accept()
        listeners.append(client)
        thread.start_new_thread(read_client, (client,))
except KeyboardInterrupt:
    pass

try:
    tivo.close()
except:
    pass
