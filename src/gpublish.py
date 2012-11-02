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

b = core.fileparser.ll_blocks(core.args.infile)

a = []
x = b
while x.next:
    a.append(x)
    x = x.next

ss = a[37]

from gntools.texts.typesetting import *

def r(s=ss, margin=72, indent=8, justify='deep'):
    rr = reform_par(ss.cont(), 'en_GB', margin=margin, indent=indent, justify=justify)
    for i in rr.splitlines():
        print(i)

r(margin=41)