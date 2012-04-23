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
import gnparser
import gp
import re

import gpconverter
import opts


if __name__ == "__main__":
    print('gneposis-publisher 0.1alpha by Adam Szieberth')
    print('='*80)

    with open(opts.declarations, encoding='utf-8') as a_file:
        rules = gp.decrules(a_file.read())
    
    with open(opts.file, encoding='utf-8') as a_file:
        raw = gpconverter.raw(a_file.read())
        
    dictionary = gp.declarations(raw, opts.decpath)
    
    struct = gp.struct(raw, rules, dictionary)
    
    
#===============================================================================
# test
#===============================================================================

    with open(opts.filepath+'/'+opts.filefile+'.raw.'+opts.fileext, 'w', encoding='utf-8') as a_raw:
        a_raw.write(raw)