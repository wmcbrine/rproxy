#!/usr/bin/env python

# Remote Proxy for TiVo, v0.3
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
__version__ = '0.3'
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

def process_queue(verbose):
    """ Pop commands from the queue and send them to the TiVo. Wait
        100ms between messages to avoid a bit jam.

    """
    while True:
        msg, address = queue.get()
        if verbose:
            sys.stderr.write('%s: %s\n' % (address, msg))
        try:
            tivo.sendall(msg)
        except:
            break
        time.sleep(0.1)

def read_client(client, address):
    """ Read commands from a client remote control program, and put them
        in the queue. Run until the client disconnects.

    """
    while True:
        try:
            msg = client.recv(1024)
        except:
            break
        if not msg:
            break
        queue.put((msg, address))
    try:
        client.close()
    except:
        pass

def status_update(address, verbose):
    """ Read status response messages from the TiVo, and send them to
        each connected client.

    """
    global tivo
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
            sys.stderr.write('%s: %s\n' % (address, status))
        for l in listeners[:]:
            try:
                l.sendall(status)
            except:
                listeners.remove(l)

def connect(target):
    """ Connect to the target TiVo within five seconds, or abort. """
    global tivo
    try:
        tivo = socket.socket()
        tivo.settimeout(5)
        tivo.connect(target)
        tivo.settimeout(None)
    except:
        raise

def serve(host_port):
    """ Listen for connections from client remote control programs;
        start new read_client() threads and add listeners as needed.
        Serve until KeyboardInterrupt.

    """
    server = socket.socket()
    server.bind(host_port)
    server.listen(5)

    try:
        while True:
            client, address = server.accept()
            listeners.append(client)
            thread.start_new_thread(read_client, (client, address))
    except KeyboardInterrupt:
        pass

def cleanup():
    """ Close all sockets, and push one last message to make the
        process_queue() thread exit.

    """
    for l in [tivo] + listeners:
        try:
            l.close()
        except:
            pass

    queue.put(('', ''))

def parse_cmdline(params):
    """ Parse the command-line options, and return tuples for host and
        target addresses, plus the verbose flag.

    """
    verbose = False
    host = ''
    port = TIVO_REMOTE_PORT1

    try:
        opts, t_address = getopt.getopt(params, 'a:p:vh', ['address=',
                                        'port=', 'verbose', 'help'])
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

    return (host, port), (t_address, t_port), verbose

def main(host_port, target, verbose=False):
    connect(target)
    thread.start_new_thread(process_queue, (verbose,))
    thread.start_new_thread(status_update, (target, verbose))
    serve(host_port)
    cleanup()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write('Must specify an address\n')
        sys.exit(1)

    host_port, target, verbose = parse_cmdline(sys.argv[1:])
    main(host_port, target, verbose)
