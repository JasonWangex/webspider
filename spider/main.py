# coding=utf-8
import sys

# spider begin
# command is
#         type      (c cleaned, t translate, d download, u url resolver)
#         address   (master ip, if master : 0)
#         port      (master port)
from multiprocessing import Value
import translate
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

    if command_type == 'c':
        translate.start_clean(port)

    elif command_type == 't':
        translate.start_trash_queue_manager(port, localShutdown)

    elif command_type == 'd':
        dispacher.start_download(address, port, localShutdown)

    elif command_type == 'u':
        dispacher.start_url_resolver(address, port, localShutdown)

    else:
        print 'can\'t start without command type'
