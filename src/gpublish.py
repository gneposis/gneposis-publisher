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

import formats

from core.args import args, infile
from gntools.lines import content
import core.fileparser
docheader = core.fileparser.get_blocks(content(infile, args.stline, args.enline))

#formats._main(docheader)

a = []
b = docheader
while b.next:
    a.append(b)
    b = b.next
