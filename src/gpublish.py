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

import core.args
import core.fileparser

a = core.fileparser.lines(core.args.infile)

l = []
i = 0
loop = True
while i <= len(a):
    l.append(core.fileparser.get_block(i, a))
    i = l[-1].lines[1] + l[-1].emptyafter + 1

b = []
for i in range(len(l)):
    b.append(l[i].content(a))

#blocks = core.fileparser.Blocks(core.args.infile)
#
#x = []
#for i in blocks:
#    x.append(i)

#raw = core.raw.make()
#import gntools.lines
#lns = gntools.lines.newlines(raw)
#import core.layout
#stm = core.layout.get_statements(raw)