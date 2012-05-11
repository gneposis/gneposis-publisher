import re

import gntools

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
    args = 0
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
            args +=1
        else:
            # If not all required arguments has benn set, you want to raise an
            # exception.
            if r > 0:
                raise Warning('Required argument missing in '+declaration+'!')
            o -= 1
            
    d['arguments'] = args
    
    return d

def layout(data, rules, dictionary, debug=False, pr=False):
    '''Creates a raw dictionary of all the declarations.
    
    usage:
    layout[line]
    , where line is the line of declaration in the data.
    
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
    # possible, and data is identical to the one the save based on. 'load'
    # function will do that. You want to force analyzation if debug is True.
    if not debug and load(data):
        if pr == True:
            print('\rGenerating layout using saved layout file...'.ljust(61),end='')
        layout = load(data)
    else:
    # Now you want to define a list for your struct elements.
        layout = []
        
        locnewlines = gntools.locnewlines(data)
        loc = 0
        line = 0
        j = 0
        while loc>=0:
            loc = data[j:].find('{')
            if loc>=0:
                previousline = line
                line = gntools.linenr(loc + j, data)
    
                j = gntools.locnewlines(data)[line+1]
    
                # Since it can be a long process, you want to put a progress
                # message.
                if pr == True:
                    print('\rGenerating layout: {0}/{1} ({2}%)'.format(line,len(locnewlines),round(line/len(locnewlines)*100,1)).ljust(61),end='')
                # You want to get the content of the current line
                _line = gntools.line(line, data)
                # Now you want to search for anything between {}-s.
                p = re.compile(r'{.+?}')
                # Since there can be more match, you want them all. 'fi' will
                # return the list of them and you will get the column from it
                fi, it = p.findall(_line), p.finditer(_line)
                if fi:
                    i = 0
                    for e in it:
                        # Add the data declaration_parser can get, first.
                        layout.append(declaration_parser(fi[i], rules, dictionary))
                        # Now the current line number in data.
                        layout[-1].update(line=line)
                        # Now the start and end column of the match.
                        layout[-1].update(column=e.span())
                        # Now you want to add css names based on key. However,
                        # you want to know if a section comes immediately after
                        # a chapter, so you can handle the vertical spaces
                        # between those titles in the css file of your html.
                        _key = declaration_parser(fi[i], rules, dictionary)['key']
                        try:
                            _previouskey = layout[-2]['key']
                        except:
                            _previouskey = None            
                        if previousline + 1 == line and _previouskey and rules[_previouskey]['options'].get('level',None) and rules[_key]['options'].get('level',None):
                            # If key follows previouskey immediately, you want
                            # css name to be the concatenation of the two.
                            layout[-1].update(css=_key+_previouskey)
                        # Now you want to include the nr of key:
                        c = 0
                        k = -1
                        loop = True
                        while loop:
                            try:
                                if layout[k]['key'] == _key:
                                    c += 1
                                    k -= 1
                                else:
                                    k -= 1
                            except:
                                loop = False
                        layout[-1].update(nr=c)
                        
#                       if rules[_key]['options'].get('level',None):
#                           layout[-1].update(ref=ref(layout,rules,layout[-1]['line']))
                            
                        i += 1
                        
            else:
                if pr == True:
                    print('\rGenerating layout: {0}/{0} (100%)'.format(len(locnewlines)).ljust(61),end='')
        
        # You want to save the layout since it is a long process to get.
        # Moreover, future calls will be fast as hell...
        save(data, layout)
    if pr == True:
        print('[DONE]'.rjust(7))
    return tuple(layout)

def get(layout, rules, startindex=0, endindex=None, oneonly=False, key=None, line=None, optionkey=None, optionvalue=None):
    def get_option(key, rules, optionkey, optionvalue):
        if optionkey and optionvalue:
            if optionvalue == rules[key]['options'].get(optionkey, False):
                return True
        elif optionkey and not optionvalue:
            if rules[key]['options'].get(optionkey, None):
                return True
        else:
            return None
           
    if not endindex:
        endindex = len(layout)
    
    result = []
    
    for i in range(startindex,endindex):
        
        if key == layout[i]['key'] and not line:
            add = True
        elif line == layout[i]['line'] and not key:
            add = True
        elif key == layout[i]['key'] and line == layout[i]['line']:
            add = True
        elif not key and optionkey and get_option(layout[i]['key'], rules, optionkey, optionvalue) and not line:
            add = True
        elif not key and optionkey and get_option(layout[i]['key'], rules, optionkey, optionvalue) and line == layout[i]['line']:
            add = True
        else:
            add = False

        if oneonly == True and add == True:
            return i
        elif oneonly == False and add == True:
            result.append(i)
    return tuple(result)

def line(data, rules, dictionary, linenr):
    _layout = layout(data,rules,dictionary)
    _declarations = get(_layout, rules, line=linenr, startindex=0, endindex=None, oneonly=False)
    _line = gntools.line(linenr,data)
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
            e = _layout[_declarations[done]]['column'][0]
            add = True
        # inter phase
        elif remaining > 0 and done > 0:
            s = _layout[_declarations[done-1]]['column'][1]
            e = _layout[_declarations[done]]['column'][0]
            add = True
        # end phase
        elif remaining == 0 and done > 0:
            s = _layout[_declarations[done-1]]['column'][1]
            e = None
            add = False
            generating = False
        
        content.append(_line[s:e])
        
        if add:
            content.append(_declarations[done])
            remaining -= 1
            done += 1

    return tuple(content)

def hasoption(rules,key,optionkey,optionvalue=None):
    if rules[key]['options'].get(optionkey,None):
        if optionvalue and rules[key]['options'][optionkey] == optionvalue:
            return True
        elif not optionvalue:
            return True
        else:
            return False
    else:
        return False
    
def optionvalues(layout, rules, optionkey='level', hierarchy=True, optionvalue=None):
    _list = []
    _set = set()
    for i in range(len(layout)):
        if hasoption(rules,layout[i]['key'],optionkey,optionvalue=optionvalue) == True:
            value = rules[layout[i]['key']]['options'][optionkey]
            _list.append(value)
            _set.add(value)
        else:
            _list.append(None)
    if hierarchy:
        _hierarchy = sorted(_set)
        for i in range(len(_list)):
            if _list[i]:
                _list[i] = _hierarchy.index(_list[i])
    return _list

def location(layout, rules, ind, continous='chapter', hierarchy=True, optionkey='level', optionvalue=None):
    def parent(layout, rules, ind, optionkey=optionkey, hierarchy=hierarchy, optionvalue=optionvalue):
        v0 = optionvalues(layout, rules, optionkey=optionkey, hierarchy=hierarchy, optionvalue=optionvalue)[ind]
        i = -1
        s = True
        while s == True and ind+i >= 0:
            v1 = optionvalues(layout, rules, optionkey=optionkey, hierarchy=hierarchy, optionvalue=optionvalue)[ind+i]
            try:
                if v1 < v0:
                    return (v0, v1, ind+i)
                else:
                    i -= 1
            except:
                i -= 1
    def count(layout, rules, ind, continous=continous, hierarchy=hierarchy, optionkey=optionkey, optionvalue=optionvalue):
        _parent = parent(layout, rules, ind, optionkey=optionkey, hierarchy=hierarchy, optionvalue=optionvalue)
        try:
            if layout[ind]['key'] in continous:
                success = True
            else:
                success = False
        except:
            success = False
                
        if success == True:
            return layout[ind]['nr']
        elif _parent:
            i = -1
            while _parent[2]+i > 0:
                v = optionvalues(layout, rules, optionkey=optionkey, hierarchy=hierarchy, optionvalue=optionvalue)[_parent[2]+i]
                if v == _parent[0]:
                    return layout[ind]['nr'] - layout[_parent[2]+i]['nr']
                else:
                    i -= 1
        return layout[ind]['nr']

    try:
        _key = layout[ind]['key']
    except:
        raise Warning('Wrong index !')


    _location = []
    loop = True
    while loop:
        _parent = parent(layout, rules, ind, optionkey=optionkey, hierarchy=hierarchy, optionvalue=optionvalue)
        _count = count(layout, rules, ind, continous=continous, hierarchy=hierarchy, optionkey=optionkey, optionvalue=optionvalue)
        
        _location.insert(0,_count)
        
        if _parent:
            ind = _parent[2]
            d = _parent[0] - _parent[1]
            while d > 1:
                _location.insert(0,None)
                d -= 1
        else:
            loop = False

    return tuple(_location)
        
def css(layout, rules, ind, argind):
    css = ''
    if layout[ind].get('css',None):
        css = layout[ind]['css']
    else:
        css = layout[ind]['key']
    if argind and argind != 0:
        try:
            arg = rules[layout[ind]['key']][min(argind,rules[layout[ind]['key']]['reqargs']+rules[layout[ind]['key']]['optargs'])]
        except:
            arg = ''
        if arg != css:
            css = css + arg
    return css