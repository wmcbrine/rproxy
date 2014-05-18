#!/usr/bin/env python

import socket
import sys
import thread
import time

TIVO_REMOTE_PORT1 = 31339

in_process = False
queue = []
listeners = []
tivo = None

def process_queue():
    global in_process
    while in_process:
        if queue:
            msg = queue.pop(0)
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

connect((sys.argv[1], TIVO_REMOTE_PORT1))

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

tivo.close()
