'''gneposis-publisher 0.1alpha by Adam Szieberth

The main purpose of this software to let authors publish their
works without any cost in different formats (coming soon).

All they need to do is to use an easy structured plain text
format which can be converted by this software.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
'''
import sys

from gntools.lines import content

import core.fileparser
from core.args import args, infile

first_block = core.fileparser.ll_blocks(content(infile, args.stline, args.enline))

if args.mode == 'plain':
    from formats.plain import main

main(first_block)
