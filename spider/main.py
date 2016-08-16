# coding=utf-8
import sys

# spider begin
# command is
#         type(m master,d only download,u only url resolver)
#         port(integer)
from multiprocessing import Value

import dispacher

if __name__ == '__main__':
    commands = sys.argv

    command_type = commands[1]
    address = commands[2]
    port = commands[3]

    localShutdown = Value('b', False)
    try:
        port = int(port)
    except ValueError:
        print 'invalid port value'

    if command_type == 'm':
        dispacher.start_master(port)

    elif command_type == 'd':
        dispacher.start_download(address, port, localShutdown)

    elif command_type == 'u':
        dispacher.start_url_resolver(address, port, localShutdown)

    else:
        print 'can\'t start without command type'
