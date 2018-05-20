#!/usr/bin/env python3
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import argparse
import handlers

# main parser
parser = argparse.ArgumentParser(description='xch command')
subparsers = parser.add_subparsers()

# bbsmenu
parser_bbsmenu = subparsers.add_parser('bbsmenu', help='see `bbsmenu -h`')
parser_bbsmenu.add_argument('-u', '--url', required=True, help='https://menu.xch.net/bbsmenu.html')
parser_bbsmenu.set_defaults(handler=handlers.command_bbsmenu)

# subback
parser_subback = subparsers.add_parser('subback', help='see `subback -h`')
parser_subback.add_argument('-u', '--url', required=True, help='http://xxx.xch.net/xxx/')
parser_subback.add_argument('--exclude-end', action='store_true', required=False, help='exclude 1001')
parser_subback.set_defaults(handler=handlers.command_subback)

# thread
parser_thread = subparsers.add_parser('thread', help='see `thread -h`')
parser_thread.add_argument('-u', '--url', required=True, help='http://xxx.xch.net/test/read.cgi/xxx/0000000000/')
parser_thread.add_argument('-r', '--range', required=False, default='l50', help='start position and range for reading. l50 (default), 100-200, 100-n')
parser_thread.add_argument('-i', '--interval', type=int, required=False, help='if this option is specified, will reload in specified sec.')
parser_thread.set_defaults(handler=handlers.command_thread)

# help
parser_help = subparsers.add_parser('help', help='see `help -h`')
parser_help.add_argument('command', help='command name which help is shown')
parser_help.set_defaults(handler=handlers.command_help)

args = parser.parse_args()
if hasattr(args, 'handler'):
    args.handler(args)
else:
    parser.print_help()
