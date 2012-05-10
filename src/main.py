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

def kindle(data, layout, rules):
    from gpconverter import kindle
    from gpconverter import utf
    body = kindle.body(data,layout, rules)
    return body
    

if __name__ == "__main__":
    print('\ngneposis-publisher 0.1alpha by Adam Szieberth, 2012')
    print('='*67)
    print('\nAnalyzing input file...'.upper())
    print('- '*33+'-')
    
    with open(opts.file, encoding='utf-8') as a_file:
        raw = gpconverter.raw(a_file.read())
    with open(opts.filepath+'/'+opts.filefile+'.raw.'+opts.fileext, 'w', encoding='utf-8') as a_raw:
        a_raw.write(raw)
    print('[DONE]'.rjust(7))

    print('\rMaking rules...'.ljust(61),end='')
    with open(opts.declarations, encoding='utf-8') as a_file:
        rules = gp.rules(a_file.read())
    print('[DONE]'.rjust(7))

    print('\rGenerating dictionary for language: {0}'.format(gp.language(raw,opts.decpath).upper()).ljust(61),end='')
    dictionary = gp.declarations(raw, opts.decpath)
    print('[DONE]'.rjust(7))
    
    layout = gp.layout.layout(raw, rules, dictionary,pr=True)
    
    if opts.mode == 'kindle':
        print('\nCreating kindle body file...'.upper())
        print('- '*33+'-')
        with open(opts.ensure_dir(opts.filepath+'/'+opts.mode)+'/'+opts.filefile+'.html', 'w', encoding='utf-8') as a_body:
            a_body.write(kindle(raw, layout, rules))
        
        
    
    
#===============================================================================
# test
#===============================================================================