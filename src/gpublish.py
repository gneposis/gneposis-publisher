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

from gntools.texts.typesetting import *

I = 2
M = 72
JUSTIFY = 'deep'
LANG = 'en_GB'

def reformat(block):

    if len(block.l_lines())==1 and M in block.centered_at():
        return block.raw_content()
    
    return reform_par(block.raw_content(), LANG, margin=M, indent=I, justify=JUSTIFY)
    

first_block = core.fileparser.ll_blocks(core.args.infile)

b = first_block
newfile = ''
                  
while b.next:
    print(b.loc)
#    newfile += reformat(b) + '\n'*(b.emptyafter + 1)
    newfile += reformat(b) + '\n'
    b = b.next

with open('test.txt',mode='w', encoding='utf-8') as test_file:
    test_file.write(newfile)                                     