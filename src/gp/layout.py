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
        s1 = re.search(r'\s*(?P<name>.+?)\s*::',declaration[i:])
        s2 = re.search(r'\s*(?P<name>.+?)\s*}',declaration[i:])
        if s1 or s2:
            if s1:
                s = s1
            else:
                s = s2
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
    # Since analization is a long process you want to import a saved layout if
    # possible, and raw_data is identical to the one the save based on. 'load'
    # function will do that. You want to force analyzation if debug is True.
    if not debug and load(raw_data):
        layout = load(raw_data)
    else:
    # Now you want to define a list for your struct elements.
        layout = []
        
        locnewlines = gnparser.locnewlines(raw_data)
        loc = 0
        j = 0
        while loc>=0:
            loc = raw_data[j:].find('{')
            line = gnparser.linenr(loc + j, raw_data)

            j += loc + 1

            i = 0
            # Since it can be a long process, you want to put a progress
            # message.
            print('\rAnalyzing input file: {0}/{1} ({2}%)'.format(line,len(locnewlines),round(line/len(locnewlines)*100,1)).ljust(61),end='')
            # You want to get the content of the current line
            _line = gnparser.line(line, raw_data)
            # Now you want to search for anything between {}-s.
            p = re.compile(r'{.+?}')
            # Since there can be more match, you want them all. 'fi' will
            # return the list of them and you will get the column from it
            fi, it = p.findall(_line), p.finditer(_line)
            if fi:
                for e in it:
                    # Add the data declaration_parser can get, first.
                    layout.append(declaration_parser(fi[i], rules, dictionary))
                    # Now the current line number in raw_data.
                    layout[-1].update(line=line)
                    # Now the start and end column of the match.
                    layout[-1].update(column=e.span())
                    i += 1
        # You want to save the layout since it is a long process to get.
        # Moreover, future calls will be fast as hell...
        save(raw_data, layout)
        print('[DONE]'.rjust(7))
    return tuple(layout)

def get(rawlayout, rules, startindex=0, endindex=None, nextonly=False, key=None, line=None, optionkey=None, optionvalue=None):
    def option(key, rules, optionkey, optionvalue):
        if optionkey and optionvalue:
            if optionvalue == rules[key]['options'].get(optionkey, False):
                return True
        elif optionkey and not optionvalue:
            if rules[key]['options'].get(optionkey, None):
                return True
        else:
            return None
           
    if not endindex:
        endindex = len(rawlayout)
    
    result = []
    
    for i in range(startindex,endindex):
        
        if key == rawlayout[i]['key'] and not line:
            add = True
        elif line == rawlayout[i]['line'] and not key:
            add = True
        elif key == rawlayout[i]['key'] and line == rawlayout[i]['line']:
            add = True
        elif not key and optionkey and option(rawlayout[i]['key'], rules, optionkey, optionvalue) and not line:
            add = True
        elif not key and optionkey and option(rawlayout[i]['key'], rules, optionkey, optionvalue) and line == rawlayout[i]['line']:
            add = True
        else:
            add = False

        if nextonly == True and add == True:
            return tuple(i)
        elif nextonly == False and add == True:
            result.append(i)
    return tuple(result)

def hierarchy(rawlayout, rules, optionkey='level'):
    _list = get(rawlayout, rules, optionkey=optionkey, startindex=0, endindex=None, nextonly=False)
    _set = set()
    for i in _list:
        _set.add(rawlayout[i]['key'])
    d={}
    for j in _set:
        d[j] = rules[j]['options'][optionkey]
    return tuple(sorted(d, key=d.get))

def depth(rawlayout, rules, key, maximum=1000, optionkey='level'):
    _hierarchy = hierarchy(rawlayout, rules, optionkey=optionkey)
    try:
        return min(_hierarchy.index(key), maximum)
    except:
        return None

def line(raw_data, rules, dictionary, linenr):
    _rawlayout = raw(raw_data,rules,dictionary)
    _declarations = get(_rawlayout, rules, line=linenr, startindex=0, endindex=None, nextonly=False)
    _line = gnparser.line(linenr,raw_data)
    remaining = len(_declarations)
    done = 0
    generating = True
    
    content = []
    
    while generating:
        # whole phase
        if remaining == 0 and done == 0:
            s = None
            e = None
            add = False
        # opening phase
        elif remaining > 0 and done == 0:
            s = None
            e = _rawlayout[_declarations[done]]['column'][0]
            add = True
        # inter phase
        elif remaining > 0 and done > 0:
            s = _rawlayout[_declarations[done-1]]['column'][1]
            e = _rawlayout[_declarations[done]]['column'][0]
            add = True
        # end phase
        elif remaining == 0 and done > 0:
            s = _rawlayout[_declarations[done-1]]['column'][1]
            e = None
            add = False
            generating = False
        
        content.append(_line[s:e])
        
        if add:
            content.append(_declarations[done])
            remaining -= 1
            done += 1

    return tuple(content)
        
        
