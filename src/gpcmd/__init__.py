import glob
import os
import re
import operator


import copy

import gnparser

def decrules(propdata):
    def get_rawdata():
        d = {}
        s1 = True
        i = 0
        while s1:
            p1 = re.compile(r'^(?!#)(?P<declaration>.+?)\s*:\s*\((?P<format>.*?)\)(?P<options>.*?)$', flags=re.M)
            s1 = p1.search(propdata[i:])
            if s1:
                d[s1.group('declaration')] = {}
                if s1.group('format') == '':
                    d[s1.group('declaration')]['format'] = None
                else:
                    d[s1.group('declaration')]['format'] = s1.group('format')
                if s1.group('options') == '':
                    d[s1.group('declaration')]['options'] = None
                else:
                    d[s1.group('declaration')]['options'] = s1.group('options')
                i += s1.end()
        return d
    prop = {}
    propkeys = list(get_rawdata().keys())
    for k in propkeys:

        prop[k] = {}
        
        propformat = get_rawdata()[k]['format']
        propoptions = get_rawdata()[k]['options']
        
        s = True
        i = 0
        nr = 1
        reqargs = 0
        optargs = 0
        while s and propformat:
            p = re.compile(r'\w+?\b')
            s = p.search(propformat[i:])
            if s:
                p2 = re.compile(r'<'+s.group()+'>')
                p3 = re.compile(r'<:: '+s.group()+'>')
                s2 = p2.search(propformat[i:])
                s3 = p3.search(propformat[i:])
                
                if s2 or s3:
                    optargs += 1
                else:
                    reqargs += 1
                prop[k][nr] = s.group()
                i += s.end()
                nr +=1
        
        prop[k]['reqargs'] = reqargs
        prop[k]['optargs'] = optargs
        
        s = True
        i = 0
        prop[k]['options'] = {}
        if propoptions:
            propoptions = propoptions+' '
        while s and propoptions:
            p = re.compile(r'\s*(.+?)\s+')
            s = p.search(propoptions[i:])
            if s:
                try:
                    prop[k]['options'][s.group(1)[:s.group(1).index('=')]] = s.group(1)[s.group(1).index('=')+1:]
                except:
                    prop[k]['options'][s.group(1)] = True
                i += s.end()    
    return prop

def declarations(inputdata, declarationspath):
    ''' Returns the declarations dictionary for inputdata'''
    def declarations_dictionary(declarationspath):
        ''' Creates the dictionary of declarations based on files in <gp.py_path>/data/languages/declarations/'''
        # You want to create a dictionary for upcoming data.
        dictionary = {}
        # Now you would like to get data from all declarations file of all
        # languages, so get their path one-by-one.
        for dict_file in glob.glob(declarationspath):
            # You need to split filename and get its language key.
            path_split = os.path.split(dict_file)
            lang = path_split[1]
            # Now you have the key you can create a subdictionary for it.
            dictionary[lang] = {}
            # Now you want to open the declarations file, and read it.
            with open(dict_file, encoding='utf-8') as a_file:
                dictfile = a_file.read()
                # Now you want to get the declaration keys from dictfile, so you
                # will use a loop and indexing.
                s = True
                i = 0
                while s:
                    # You want to search for a row which is not starting with an #,
                    # but contains the declaration followed by a : with zero or
                    # more whitespace(s) before and after followed by the key part
                    # until the end of the line (excluding trailing whitespaces).
                    p = re.compile(r'^(?!#)(?P<declaration>.+?)\s{0,}:\s{0,}(?P<key>.+?)\s{0,}$', flags=re.M)
                    # You want to search for the pattern in the file from the
                    # actual index to the end. If no match, 's' returns None and
                    # the loop will stop.
                    s = p.search(dictfile[i:])
                    if s:
                        # If match then you want to add the declaration to the
                        # dictionary.
                        dictionary[lang][s.group('declaration')] = s.group('key')
                        # Now you want to increment the index with the end of the
                        # match.
                        i += s.end()
        return dictionary
    def get_language(inputdata, declarationspath):
        ''' Gets language key from beginning of inputdata:
        
        If inputdata begins with '{hu}' or '{HU}' it returns 'hu' if there is a
        hu file in /data/languages/declarations/.
        
        If inputdata begins with '{AUTHOR ...}' or '{TITLE ...}' it returns
        'en' since it will find AUTHOR or TITLE as a valid author or title 
        declaration in the english declaration file. Same with '{SZERZŐ ...}'
        for hungarian; this returns 'hu'.
        '''
        # You want to search for the very first declaration of inputdata.
        s = re.search(r'^{(?P<key>.+?)\s|}', inputdata)
        # Now you want to check all languages. 'k' returns their keys.
        for k in list(declarations_dictionary(declarationspath).keys()):
            # If the very first declaration is the actual key, you are done.
            # This works for '{HU}' kind language declaration.  
            if s.group('key').lower() == k:
                return k
            # Else you want to check all the keys of the actual language for
            # matching. 
            else:
                for l in list(declarations_dictionary(declarationspath)[k].keys()):
                    if s.group('key') == l:
                        # Now you only want allow 'k' to be the language if
                        # the respectable value in the dictionary is 'author'
                        # or 'title'.
                        if declarations_dictionary(declarationspath)[k][l] == 'author' or declarations_dictionary(declarationspath)[k][l] == 'title':
                            return k
    # You want this function to return the dictionary for the document language
    # only.
    
    return declarations_dictionary(declarationspath)[get_language(inputdata, declarationspath)]

def decparser(declaration, rules, dictionary):
    def key(declaration, dictionary):
        p = re.compile(r'{(?P<key>.+?)[\s}]')
        s = p.search(declaration)
        e = re.search(gnparser.restg(s.group('key')),declaration)
        return (dictionary[s.group('key')], e.end()+1)
    d = {}
    key = key(declaration, dictionary)
    d['key'] = key[0]
    i = key[1]
    opts = rules[key[0]]
    r = opts['reqargs']
    o = opts['optargs']
    a = r + o
    while r + o > 0:
        name = opts[a-r-o+1]
        s = re.search(r'\s*(?P<name>.+?)\s*[:}]',declaration[i:])
        if s:
            d[name] = s.group('name')
            i += s.end()+1
            if r > 0:
                r -= 1
            else:
                o -= 1
        else:
            # ide kell egy raise ha r nagyobb 0
            o -= 1
    return d

def rawstruct(inputdata, rules, dictionary):
    def nextdeclaration(inputdata, rules, dictionary, startline, declaration):
        locnewlines = gnparser.locnewlines(inputdata)
        for line in range(startline, len(locnewlines)+1):
            if inputdata[locnewlines[line]] == '{':
                if not declaration or declaration == decparser(gnparser.line(line, inputdata), rules, dictionary)['key']:
                    return line
    rawstruct = {}
    locnewlines = gnparser.locnewlines(inputdata)
    for line in locnewlines:
        if inputdata[locnewlines[line]] == '{':
            rawstruct[line] = decparser(gnparser.line(line, inputdata), rules, dictionary)
            rawstruct[line].update(nextdeclaration=nextdeclaration(inputdata, rules, dictionary, line+1, None))
            rawstruct[line].update(nextsamedeclaration=nextdeclaration(inputdata, rules, dictionary, line+1, rawstruct[line]['key']))
    return rawstruct

def l_lines(rawstruct):
    return sorted(list(rawstruct.keys()))

def s_rules(rawstruct):
    s = set()
    for line in l_lines(rawstruct):
        s.add(rawstruct[line]['key'])
    return s

def struct(rawstruct):
    struct = {}
    _rawstruct = copy.deepcopy(rawstruct)
    for rule in s_rules(_rawstruct):
        struct[rule] = {}
        i = 1
        j = 0
        for line in l_lines(_rawstruct):
            if rule == _rawstruct[line].get('key', False):
                del _rawstruct[line]['key']
                struct[rule][i] = _rawstruct[line]
                struct[rule][i].update(line=line, structindex=j)
                i += 1
            j += 1
    return struct

def g_dec_by_opt(rules,option):
    s = set(rules.keys())
    d = set()
    for e in s:
        if rules[e]['options'].get(option,None):
            d.add(e)
    return d

def g_rule(rawstruct, rules):
    l = list(g_dec_by_opt(rules,'level') & s_rules(rawstruct))
    level = []
    for i in l:
        level.append(rules[i]['options']['level'])
    d = dict(zip(l,level))
    return tuple(sorted(d, key=d.get))

def sub(rawstruct, rules, lineofdeclaration):
    rule = g_rule(rawstruct,rules)
    i = l_lines(rawstruct).index(lineofdeclaration)
    refdeclaration = rawstruct[lineofdeclaration]['key']
    if refdeclaration in rule:
        refdeclarationindex = rule.index(refdeclaration)
        s = True
        sub = []
        while s and i < len(l_lines(rawstruct))-1:
            i += 1
            currentline = l_lines(rawstruct)[i]
            currentdeclaration = rawstruct[currentline]['key']
            currentdeclarationindex =rule.index(currentdeclaration)
            if currentdeclarationindex == refdeclarationindex+1:
                sub.append(currentline)
            elif currentdeclarationindex <= refdeclarationindex:
                s = False
    else:
        return None
    return tuple(sub)

def bodystruct(rawstruct, rules, depth=None):
    hier = g_rule(rawstruct,rules)
    if not depth:
        depth=len(hier)
    for line in l_lines(rawstruct):
        if rawstruct[line]['key'] in hier[0:depth]:
            print('    '*hier.index(rawstruct[line]['key'])+rawstruct[line]['title'])
    return None

# map(str, list_of_ints)
#===============================================================================
# temporary
#===============================================================================

########## This goes to some verifying function
#   def options(declaration, rules):
#       return list(rules['declaration']['options'].keys())
#   def option(declaration, option):
#       return declaration.get('option', False)