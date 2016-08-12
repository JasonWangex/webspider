# coding=utf-8
import sys

# spider begin
# command is
#         type(m master,d only download,u only url resolver)
#         port(integer)
import dispacher

if __name__ == '__main__':
    commands = sys.argv

    command_type = commands[1]
    port = commands[2]

    try:
        port = int(port)
    except ValueError:
        print 'invalid port value'

    if command_type == 'm':
        dispacher.start_master(port)

    elif command_type == 'd':
        dispacher.start_download(port)

    elif command_type == 'u':
        dispacher.start_url_resolver(port)

    else:
        print 'can\'t start without command type'
