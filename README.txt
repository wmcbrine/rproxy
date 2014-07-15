Remote Proxy for TiVo, v0.5
by William McBrine <wmcbrine@gmail.com>
June 17, 2014

This is a server that connects to the "Crestron" interface (port 31339) 
on a Series 3 or later TiVo, and reflects the port back out, allowing 
multiple simultaneous client connections. (The TiVo itself only allows 
one connection to the remote service at a time.) It queues commands from 
all sources, and sends them to the TiVo no more than once every tenth of 
a second, to avoid crashing the TiVo; and it sends status responses back 
to all connected clients. You can also monitor commands and responses on 
the console. And you can run it on a non-standard port, if your remote 
control program supports that. (Example use: run proxies for multiple 
TiVos on the same machine, using a different port for each.)

Note that rproxy only supports the port 31339 interface, not the more 
advanced interface used by TiVo's own iOS and Android apps and KMTTG. 
But most third-party apps use this older interface. To use rproxy, you 
must first enable the interface on the TiVo, and you need one or more 
appropriate remote apps, such as my Network Remote.

Like my other TiVo apps, rproxy relies on Python 2.x (standard with OS X 
and Linux, otherwise available from http://python.org/ .)

Remote Proxy was inspired by this TCF thread:

http://www.tivocommunity.com/tivo-vb/showthread.php?t=517604


Quick Start
-----------

From a command line:

  python rproxy.py <your.tivo.ip.here>

Or, you can skip the IP address, and specify "-i" to make rproxy scan 
the network for TiVos and provide a list.

When you're done proxying: Ctrl-C (or just close the command window).


Command-Line Options
--------------------

-a, --address      Specify the address to serve from. The default is
                   '' (bind to all interfaces).

-p, --port         Specify the port to serve from. The default is
                   31339, the standard TiVo "Crestron" remote port.

-l, --list         List TiVos found on the network, and exit.

-i, --interactive  List TiVos found, and prompt which to connect to.

-f, --first        Scan the network and connect to the first available
                   TiVo. Ignores proxies.

-z, --nozeroconf   Disable Zeroconf announcements.

-v, --verbose      Echo messages to and from the TiVo to the console.
                   (In combination with -l, show extended details.)

-x, --exitdc       Exit on disconnection from the TiVo (e.g. it reboots). 
                   Absent this option, rproxy will attempt to reconnect.

-h, --help         Print help and exit.

<address>          Any other command-line option is treated as the name,
                   TiVo Service Number, or IP address (with optional
                   port number) of the TiVo to connect to. This is a
                   required parameter, except with -l, -i, -f or -h.


Changes
-------

0.5  -- TiVos can now be specified on the command line by name (i.e. the
        display name, as seen in the "My Shows" list, or via -l -- not
        to be confused with the DNS name, which also works), or by TiVo
        Service Number, as well as by IP. Based on a suggestion by
        "telemark".

        New option "-f" (or "--first") to do a scan and connect to the
        first TiVo found. For the many single-TiVo networks out there.
        This will skip over both already-proxied TiVos (as with -i), but
        also the proxies themselves.

        Specifying the port on the command line via colon notation (i.e.
        "tivoip:31339") was actually broken since 0.2.

        Better reporting of various error conditions.

0.4  -- Automatic discovery of TiVos, via the interactive (-i) and list
        (-l) options, so you don't need to know your TiVo's address
        beforehand. Already-proxied TiVos are recognized, and excluded
        from the interactive menu. Note that (unlike my Network Remote)
        this uses Zeroconf exclusively.

        In the event that the properties of the connected TiVo aren't
        available (perhaps due to Zeroconf failure), rproxy now provides
        a more complete set of phony details in its own announcements.

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
