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
        line = 0
        j = 0
        while loc>=0:
            loc = raw_data[j:].find('{')
            if loc>=0:
                previousline = line
                line = gnparser.linenr(loc + j, raw_data)
    
                j = gnparser.locnewlines(raw_data)[line+1]
    
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
                    i = 0
                    for e in it:
                        # Add the data declaration_parser can get, first.
                        layout.append(declaration_parser(fi[i], rules, dictionary))
                        # Now the current line number in raw_data.
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
                        elif rules[_key]['options'].get('level',None) :
                            layout[-1].update(css=_key)
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
                print('\rAnalyzing input file: {0}/{0} (100%)'.format(len(locnewlines)).ljust(61),end='')
        
        # You want to save the layout since it is a long process to get.
        # Moreover, future calls will be fast as hell...
        save(raw_data, layout)
        print('[DONE]'.rjust(7))
    return tuple(layout)

def get(rawlayout, rules, startindex=0, endindex=None, nextonly=False, key=None, line=None, optionkey=None, optionvalue=None):
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
        endindex = len(rawlayout)
    
    result = []
    
    for i in range(startindex,endindex):
        
        if key == rawlayout[i]['key'] and not line:
            add = True
        elif line == rawlayout[i]['line'] and not key:
            add = True
        elif key == rawlayout[i]['key'] and line == rawlayout[i]['line']:
            add = True
        elif not key and optionkey and get_option(rawlayout[i]['key'], rules, optionkey, optionvalue) and not line:
            add = True
        elif not key and optionkey and get_option(rawlayout[i]['key'], rules, optionkey, optionvalue) and line == rawlayout[i]['line']:
            add = True
        else:
            add = False

        if nextonly == True and add == True:
            return tuple(i)
        elif nextonly == False and add == True:
            result.append(i)
    return tuple(result)

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

def declinopt(rawlayout,rules, optionkey):
    _list = get(rawlayout, rules, optionkey=optionkey, startindex=0, endindex=None, nextonly=False)
    _set = set()
    for i in _list:
        _set.add(rawlayout[i]['line'])
    return sorted(_set)

def decopt(rawlayout, rules, optionkey, hierarchy=False):
    _list = declinopt(rawlayout, rules, optionkey=optionkey)
    d={}
    _set = set()
    for i in _list:
        for j in range(len(rawlayout)):
            if rawlayout[j]['line'] == i and rules[rawlayout[j]['key']]['options'].get(optionkey, None): 
                d[i] = rules[rawlayout[j]['key']]['options'][optionkey]
                _set.add(rules[rawlayout[j]['key']]['options'][optionkey])
    if hierarchy:
        _hierarchy = sorted(_set)
        for j in d:
            d[j] = _hierarchy.index(d[j])
    return d

def option(rawlayout,rules,line, hierarchy=False, optionkey='class'):
    _declinesbyoption = declinopt(rawlayout,rules, optionkey=optionkey)
    if line < min(_declinesbyoption):
        return None
    elif line in _declinesbyoption:
        return None
    elif line > max(_declinesbyoption):
        _line = _declinesbyoption[len(_declinesbyoption)-1]
        return decopt(rawlayout, rules, optionkey, hierarchy=hierarchy)[_line]
    else:
        for i in range(len(_declinesbyoption)):
            _line = _declinesbyoption[i]
            _nextline = _declinesbyoption[i+1]
            if _line < line and _nextline > line:
                return decopt(rawlayout, rules, optionkey, hierarchy=hierarchy)[_line]

def ref(rawlayout,rules, line, hierarchy=True, optionkey='level'):
    
    _declinesbyoption = declinopt(rawlayout,rules, optionkey=optionkey)
    
    def parent(rawlayout,rules, line, hierarchy=True, optionkey='level'):
        i = _declinesbyoption.index(line)
        v0 = decopt(rawlayout,rules,optionkey,hierarchy=hierarchy)[line]
        s = True
        while s:
            try:
                _line = _declinesbyoption[i-1]
                v1 = decopt(rawlayout,rules,optionkey,hierarchy=hierarchy)[_line]
                if v1 < v0:
                    return (v0, v1, _line)
                else:
                    i -= 1
            except:
                s = False
    
    def count(rawlayout, rules, line, startline=None):
        def startlineind(rawlayout,startline):
            for i in rawlayout:
                if i['line'] >= startline:
                    return rawlayout.index(i)
            return 0
        
        for i in rawlayout:
            if i['line'] == line:
                _key =  i['key']
        
        if startline:
            j = startlineind(rawlayout,startline)
        else:
            j = 0
        
        c = 1
        
        for k in range(j,len(rawlayout)):
            if rawlayout[k]['key']==_key and rawlayout[k]['line']==line:
                return c
            elif rawlayout[k]['key']==_key:
                c += 1
    
    
    ref = []
    loop = True
    while loop:
        if line in _declinesbyoption:
            _parent = parent(rawlayout, rules, line, hierarchy=hierarchy, optionkey=optionkey)
            
            _count = count(rawlayout, rules, line)
            
            if _parent:
                _countfromparent = count(rawlayout, rules, line, startline=_parent[2])
                if _count == _countfromparent:
                    ref.insert(0,_count)
                else:
                    ref.insert(0,(_count, _countfromparent))
            else:
                ref.insert(0,_count)
            
            if _parent:
                line = _parent[2]
                d = _parent[0] - _parent[1]
                while d > 1:
                    ref.insert(0,None)
                    d -= 1
            else:
                loop = False
        else:
            loop = False
    
    return tuple(ref)