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

print('\ngneposis-publisher 0.1alpha by Adam Szieberth, 2012')
print('='*67)

import sys

import core.raw
raw = core.raw.make()
import gntools.lines
lns = gntools.lines.newlines(raw)
import core.layout
stm = core.layout.get_statements(raw)