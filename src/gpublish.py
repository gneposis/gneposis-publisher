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

from core.opts import decmainpath, decpath, ensure_dir, file, fileext, filefile, filepath, mode
from formats import kindle
from layout.create import layout
from layout.declarat import dictionary
from layout.language import language
from layout.rawize import rawize
from layout.rules import rules

if __name__ == "__main__":
    print('\ngneposis-publisher 0.1alpha by Adam Szieberth, 2012')
    print('='*67)
    print('\nAnalyzing input file...'.upper())
    print('- '*33+'-')
    
    with open(file, encoding='utf-8') as a_file:
        raw = rawize(a_file.read())
    with open(filepath+'/'+filefile+'.raw.'+fileext, 'w', encoding='utf-8') as a_raw:
        a_raw.write(raw)
    print('[DONE]'.rjust(7))

    print('\rMaking rules...'.ljust(61),end='')
    with open(decmainpath, encoding='utf-8') as a_file:
        rules = rules(a_file.read())
    print('[DONE]'.rjust(7))

    print('\rGenerating dictionary for language: {0}'.format(language(raw,decpath).upper()).ljust(61),end='')
    dictionary = dictionary(raw, decpath)
    print('[DONE]'.rjust(7))
    
    layout = layout(raw, rules, dictionary,pr=True)
    
    if mode == 'kindle':
        print('\nCreating kindle body file...'.upper())
        print('- '*33+'-')
        with open(ensure_dir(filepath+'/'+mode)+'/'+filefile+'.html', 'w', encoding='utf-8') as a_body:
            a_body.write(kindle.body(raw, layout, rules))
        
        
    
    
#===============================================================================
# test
#===============================================================================