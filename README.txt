Remote Proxy for TiVo, v0.3
by William McBrine <wmcbrine@gmail.com>
May 26, 2014

This is a very simple server that connects to the "Crestron" interface 
(port 31339) on a Series 3 or later TiVo, and reflects the port back 
out, allowing multiple simultaneous connections. (The TiVo itself only 
allows one connection to the remote service at a time.) Commands are 
queued from all sources, and sent to the TiVo no more often than once 
every tenth of a second, to avoid crashing the TiVo. Status responses 
are sent back to all connected clients. In other words, it makes the 
remote control service work the way the spec PDF already says that it's 
supposed to. :) You also have the option of monitoring the commands and 
responses on the console. And you can run it on a non-standard port, if 
your remote control program supports that. (Example use: run proxies for 
multiple TiVos on the same machine, using a different port for each.)

Note that this only supports the original port 31339 interface, not the 
more advanced interface used by TiVo's own iOS and Android apps, as well 
as by KMTTG. But most third-party apps use the older interface. To use 
the proxy, you must of course first enable the interface on the TiVo, 
and you need one or more appropriate remote apps. By itself, the proxy 
does nothing. (I assume anyone trying this program is already a user of 
remote control apps for the TiVo, and knows why they want it.)

Currently the proxy doesn't announce itself, so you have to enter its 
address (i.e. the address of the computer where it's running) into the 
remote app(s) manually.

Like my other TiVo apps, this program relies on Python 2.x (standard 
with OS X and Linux, otherwise available from http://python.org/ .)

Remote Proxy was inspired by this TCF thread:

http://www.tivocommunity.com/tivo-vb/showthread.php?t=517604


Quick Start
-----------

From a command line:

  python rproxy.py <your.tivo.ip.here>

(Assuming you already have Python installed, the TiVo's remote service 
active, etc.) When done: Ctrl-C (or just close it). Actual example:

  python rproxy.py 192.168.1.73

(or just ./rproxy.py <ip> on *nix)


Command-Line Options
--------------------

-a, --address     Specify the address to serve from. The default is
                  '' (bind to all interfaces).

-p, --port        Specify the port to serve from. The default is
                  31339, the standard TiVo "Crestron" remote port.

-z, --nozeroconf  Disable Zeroconf announcements.

-v, --verbose     Echo messages to and from the TiVo to the console.

-h, --help        Print help and exit.

<address>         Any other command-line option is treated as the IP
                  address (with optional port number) of the TiVo to
                  connect to. This is a required parameter.


Changes
-------

0.3  -- Announce the service via Zeroconf, making it auto-discoverable. 
        (It appears as "Proxy(tivoname)".) Can be suppressed via -z, or 
        by removing Zeroconf.py.

        The verbose mode display now includes the IP and port of the 
        system where the command or response originated.

        Slightly reorganized and better-documented.

0.2  -- Changed from list/wait loop to Queue.Queue. Suggestion of 
        "telemark".

        Added verbose mode (log commands and responses to the console).

        Allow host address and port to be specified.

        Reorganized and documented.
