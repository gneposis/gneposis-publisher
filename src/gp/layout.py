import re

import gnparser

from .pickler import load,save
        
def declaration_parser(declaration, rules, dictionary):
    '''Parses a declaration string.
    
    For example
    decparser('{CHAPTER First Chapter :: The Dog}', <rules>, <dictionary>)
    can return
    {'subtitle': 'The Dog', 'key': 'chapter', 'title': 'First Chapter'}
    if rules and dictionary are default and english.
    Same return can be produced using a hungarian dictionary and the declaration:
    '{FEJEZET First Chapter :: The Dog}'
    '''
    def key(declaration, dictionary):
        '''Parses the key of the declaration.'''
        # You want to search for an "{" followed by any sequence until a
        # whitespace or a closin "}".
        p = re.compile(r'{(?P<key>.+?)[\s}]')
        s = p.search(declaration)
        # Now you have the declaration which has to be translated using
        # the dictionary. Plus you also want to return the index of the end of
        # the key.
        return (dictionary[s.group('key')], s.end())
    # Now let's start to parse your declaration! A new dictionary for it
    # the key including
    d = {}
    key = key(declaration, dictionary)
    d['key'] = key[0]
    # You want to point your index _after_ the declaration key in your
    # declaration string. 
    i = key[1]
    # You want to know if the arguments are required or optional ones, and if
    # all the required arguments has been declared.
    rule = rules[key[0]]
    # So r will show how many required argument remained, similar to o for
    # optionals. a shows the total of arguments.
    r = rule['reqargs']
    o = rule['optargs']
    a = r + o
    while r + o > 0:
        # You get the name of the current argument. Index: Total - current + 1.
        name = rule[a-r-o+1]
        # You search for a complete sequence excluding whitespaces followed by
        # a ":" or a closing "}".
        s = re.search(r'\s*(?P<name>.+?)\s*[:}]',declaration[i:])
        if s:
            # If match then you add the argument to the dictionary, increment
            # the search index, and check if r or o should be decreased by one.
            d[name] = s.group('name')
            i += s.end()+1
            if r > 0:
                r -= 1
            else:
                o -= 1
        else:
            # If not all required arguments has benn set, you want to raise an
            # exception.
            if r > 0:
                raise Warning('Required argument missing in '+declaration+'!')
            o -= 1
    return d

def raw(raw_data, rules, dictionary, debug=False):
    '''Creates a raw dictionary of all the declarations.
    
    usage:
    layout[line]
    , where line is the line of declaration in the raw_data.
    
    For example:
    layout[1]
    returns
    {'nextsamedeclaration': None, 'nextdeclaration': 2, 'name': 'Jane Austen',
        'key': 'author', 'sortname': 'Austen, Jane'}
    
    key shows the declaration key
    nextdeclaration shows the line of the next declaration.
    nextsamedeclaration shows the line of the next identical declaration
    if any.
    remaining keys are determined by rules
    '''
    if not debug and load(raw_data):
        layout = load(raw_data)
    else:
    # Now you want to define a list for your struct elements.
        layout = []
        # Now you want to get the locations of all the newlines of raw_data and
        # parse them one-by-one if they contain a declaration.
        locnewlines = gnparser.locnewlines(raw_data)
        for line in locnewlines:
            i = 0
            print('\rAnalizing input file: {0}/{1} ({2}%)'.format(line,len(locnewlines),round(line/len(locnewlines)*100,1)).ljust(61),end='')
            _line = gnparser.line(line, raw_data)
            p = re.compile(r'{.+?}')
            fi, it = p.findall(_line), p.finditer(_line)
            
            if fi:
                for e in it:
                    layout.append(declaration_parser(fi[i], rules, dictionary))
                    layout[-1].update(line=line)
                    layout[-1].update(column=e.span())
                    i += 1
        save(raw_data, layout)
        print('[DONE]'.rjust(7))
    return tuple(layout)

