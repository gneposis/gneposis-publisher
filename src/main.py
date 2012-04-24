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

import gp.layout

def kindle(data, struct):
    from gpconverter import kindle
    from gpconverter import utf
    a = kindle.body(data,struct)
    return a
    

if __name__ == "__main__":
    print('\ngneposis-publisher 0.1alpha by Adam Szieberth, 2012')
    print('='*67)

    print('\nAnalyzing input file...'.ljust(61),end='')
    with open(opts.declarations, encoding='utf-8') as a_file:
        rules = gp.decrules(a_file.read())
    
    with open(opts.file, encoding='utf-8') as a_file:
        raw = gpconverter.raw(a_file.read())
        
    dictionary = gp.declarations(raw, opts.decpath)
    
    struct = gp.struct(raw, rules, dictionary)
    print('[DONE]'.rjust(7))
    
    if opts.mode == 'kindle':
        print('\nCreating kindle body file...'.ljust(61),end='')
        with open(opts.ensure_dir(opts.filepath+'/'+opts.mode)+'/'+opts.filefile+'.html', 'w', encoding='utf-8') as a_body:
            a_body.write(kindle(raw, struct))
        print('[DONE]'.rjust(7))
        
        
    
    
#===============================================================================
# test
#===============================================================================

    with open(opts.filepath+'/'+opts.filefile+'.raw.'+opts.fileext, 'w', encoding='utf-8') as a_raw:
        a_raw.write(raw)