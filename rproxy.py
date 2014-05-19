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

    Command-line options:

    -a, --address     Specify the address to serve from. The default is
                      '' (bind to all interfaces).

    -p, --port        Specify the port to serve from. The default is
                      31339, the standard TiVo "Crestron" remote port.

    -v, --verbose     Echo messages to and from the TiVo to the console.

    -h, --help        Print help and exit.

    <address>         Any other command-line option is treated as the IP
                      address (with optional port number) of the TiVo to
                      connect to. This is a required parameter.

"""

__author__ = 'William McBrine <wmcbrine@gmail.com>'
__version__ = '0.2'
__license__ = 'GPL'

import getopt
import socket
import sys
import thread
import time

from Queue import Queue

TIVO_REMOTE_PORT1 = 31339

queue = Queue()
listeners = []
tivo = None
verbose = False

def process_queue():
    while True:
        msg = queue.get()
        if verbose:
            sys.stderr.write('%s\n' % msg)
        try:
            tivo.sendall(msg)
        except:
            break
        time.sleep(0.1)

def read_client(client):
    while True:
        try:
            msg = client.recv(1024)
        except:
            break
        if not msg:
            break
        queue.put(msg)
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

host = ''
port = TIVO_REMOTE_PORT1

if len(sys.argv) < 2:
    sys.stderr.write('Must specify an address\n')
    sys.exit(1)

try:
    opts, t_address = getopt.getopt(sys.argv[1:], 'a:p:vh',
                                    ['address=', 'port=', 'verbose', 'help'])
except getopt.GetoptError, msg:
    sys.stderr.write('%s\n' % msg)

for opt, value in opts:
    if opt in ('-a', '--address'):
        host = value
    elif opt in ('-p', '--port'):
        port = int(value)
    elif opt in ('-v', '--verbose'):
        verbose = True
    elif opt in ('-h', '--help'):
        print __doc__
        sys.exit()

t_address = t_address[0]
if ':' in t_address:
    t_address, t_port = address.split(':')
    t_port = int(t_port)
else:
    t_port = TIVO_REMOTE_PORT1
connect((t_address, t_port))

thread.start_new_thread(process_queue, ())
thread.start_new_thread(status_update, ())

server = socket.socket()
server.bind((host, port))
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
