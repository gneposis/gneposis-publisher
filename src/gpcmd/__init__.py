import glob
import os
import re
import operator

import copy

import gnparser

def decrules(propdata):
    '''Parses rules from a rules file'''
    def get_rawdata():
        '''This function does the first phase:
        It separates a declaration line to declaration, format, and options.
        
        An example declaration line:
        chapter : (title <:: subtitle>) main level=3
        
        declaration: "chapter"
        format: "title <:: subtitle>
        options: "main level=3"
        
        Lines starting with "#" are ignored to comments.
        '''
        d = {}
        s = True
        # This index will show you where to start parsing
        i = 0
        while s:
            # You use a regular expression to separate the parts of the
            # declarations line
            p = re.compile(r'^(?!#)(?P<declaration>.+?)\s*:\s*\((?P<format>.*?)\)(?P<options>.*?)$', flags=re.M)
            # s returns None if no match which stops the loop
            s = p.search(propdata[i:])
            if s:
                # If match you want to define a subdictionary for that
                # particular declaration
                d[s.group('declaration')] = {}
                # Now you want to put the parts into the dictionary 
                if s.group('format') == '':
                    d[s.group('declaration')]['format'] = None
                else:
                    d[s.group('declaration')]['format'] = s.group('format')
                if s.group('options') == '':
                    d[s.group('declaration')]['options'] = None
                else:
                    d[s.group('declaration')]['options'] = s.group('options')
                # And of course you increment i to exclude this declaration
                # from future searches.
                i += s.end()
        return d
    # Now you want to go step 2 and separate the levels of the rawdata to make
    # a nice dictionary of the rules. You want to create a new dictionary for
    # the rules, and add the declarations one-by-one to it, nicely structured.
    prop = {}
    propkeys = list(get_rawdata().keys())
    for k in propkeys:
        prop[k] = {}
        # You want to work with the parts of rawdata, so you get them.
        propformat = get_rawdata()[k]['format']
        propoptions = get_rawdata()[k]['options']
        # First you want to start with the format part. You want to know how
        # many required arguments are (if any) and how many optional arguments
        # can follow them (if any).
        s = True
        i = 0
        # You are searching for the first argument
        nr = 1
        reqargs = 0
        optargs = 0
        # If propformat is None, there are nothing to do here, otherwise start
        # parsing.
        while s and propformat:
            # You are searching for complete words, and one only
            p = re.compile(r'\w+?\b')
            s = p.search(propformat[i:])
            if s:
                # If there is a match, you want to know if it is an optional
                # argument as the first argument... 
                p2 = re.compile(r'<'+s.group()+'>')
                s2 = p2.search(propformat[i:])
                # Or following another argument:   
                p3 = re.compile(r'<:: '+s.group()+'>')
                s3 = p3.search(propformat[i:])
                if s2 or s3:
                    # If optional, you want to increment optargs, else reqargs
                    optargs += 1
                else:
                    reqargs += 1
                # Now you can add the argument to the dictionary...
                prop[k][nr] = s.group()
                # Exclude it from future searches
                i += s.end()
                # And looking for the next rule
                nr +=1
        # If done you add reqargs and optargs to your dictionary
        prop[k]['reqargs'] = reqargs
        prop[k]['optargs'] = optargs
        # Now you want to parse options.
        s = True
        i = 0
        prop[k]['options'] = {}
        # It will be easier to parse options if you force them to have a
        # whitespace at their ends.
        if propoptions:
            propoptions = propoptions+' '
        while s and propoptions:
            # See? You want to search for any continuous string sequence
            # followed by a whitespace. This lets you to handle "="-s.
            p = re.compile(r'\s*(.+?)\s+')
            s = p.search(propoptions[i:])
            if s:
                try:
                    try:
                        # Now you try to handle "option" = int kind of options.
                        prop[k]['options'][s.group(1)[:s.group(1).index('=')]] = int(s.group(1)[s.group(1).index('=')+1:])
                    except:
                        # Noy you try to handle "option" = str kind of options
                        prop[k]['options'][s.group(1)[:s.group(1).index('=')]] = s.group(1)[s.group(1).index('=')+1:]
                except:
                    # If none above works you simply want to make your option as True
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

def rawstruct(rawdata, rules, dictionary):
    '''Creates a raw dictionary of all the declarations.
    
    usage:
    rawstruct[line]
    , where line is the line of declaration in the rawdata.
    
    For example:
    rawstruct[1]
    returns
    {'nextsamedeclaration': None, 'nextdeclaration': 2, 'name': 'Jane Austen',
        'key': 'author', 'sortname': 'Austen, Jane'}
    
    key shows the declaration key
    nextdeclaration shows the line of the next declaration.
    nextsamedeclaration shows the line of the next identical declaration
    if any.
    remaining keys are determined by rules
    '''
    def nextdeclaration(rawdata, rules, dictionary, startline, key=None):
        '''This function is to calculate line number of the next declaration
        based on key (any if key=None) and startline.'''
        # You want to get the locations of all the newlines of rawdata.
        locnewlines = gnparser.locnewlines(rawdata)
        # Now you want to check all lines from startline to the end of data if
        # they start with an "{".
        for line in range(startline, len(locnewlines)+1):
            if rawdata[locnewlines[line]] == '{':
                # Now if no key has been defined, the first one is returned.
                # Otherwise its key should be the same as given.
                if not key or key == decparser(gnparser.line(line, rawdata), rules, dictionary)['key']:
                    return line
    # Now you want to define a dictionary for your struct data.
    rawstruct = {}
    # Now you want to get the locations of all the newlines of rawdata and
    # parse them one-by-one if they contain a declaration.
    locnewlines = gnparser.locnewlines(rawdata)
    for line in locnewlines:
        if rawdata[locnewlines[line]] == '{':
            # You want to add all the data gnparser could get of the
            # declaration itself...
            rawstruct[line] = decparser(gnparser.line(line, rawdata), rules, dictionary)
            # Now you want to include nextdeclaration,
            rawstruct[line].update(nextdeclaration=nextdeclaration(rawdata, rules, dictionary, line+1))
            # and the next identicaldeclaration
            rawstruct[line].update(nextsamedeclaration=nextdeclaration(rawdata, rules, dictionary, line+1, rawstruct[line]['key']))
    return rawstruct

def l_lines(rawstruct):
    '''Returns a sorted list of the line numbers of declarations.
    Useful to iterate elements of rawstruct.'''
    return sorted(list(rawstruct.keys()))

def s_rules(rawstruct):
    '''Returns a set of all different declaration keys of rawstruct.'''
    s = set()
    for line in l_lines(rawstruct):
        s.add(rawstruct[line]['key'])
    return s

def struct(rawstruct):
    '''Orders rawstruct by keys.
    
    For example:
    struct(rawstruct)['chapter'][1]
    can return:
    {'nextdeclaration': 46, 'title': 'Chapter 1', 'nextsamedeclaration': 46,
        'line': 11, 'structindex': 3}
    
    some of the data are same as rawstruct[11] (see line!), but
    line shows the line of that declaration in rawdata
    structindex shows the index of that declaration in the list of all
    declarations.
    '''
    struct = {}
    # You want to copy rawstruct but not modify it with future alterations.
    _rawstruct = copy.deepcopy(rawstruct)
    # Now you want to parse rawdata ordered by declaration keys.
    for rule in s_rules(_rawstruct):
        struct[rule] = {}
        # i for the identical declarations
        i = 1
        # j for any declarations
        j = 0
        # Now you want to check all lines of rawstruct for a definition same as
        # current rule.
        for line in l_lines(_rawstruct):
            # You want to use get() since you want to get rid of 'key' keys in
            # struct. This is why you delete them as soon as you find a new
            # declaration to parse: This would raise an exception for future
            # parsing. Get solves that. And this is why you wanted to work with
            # the copy of rawstruct.
            if rule == _rawstruct[line].get('key', False):
                del _rawstruct[line]['key']
                struct[rule][i] = _rawstruct[line]
                # Now you add line and index to struct.
                struct[rule][i].update(line=line, structindex=j)
                i += 1
            j += 1
    return struct

def g_dec_by_opt(rules,option):
    '''Returns the set of all the rule keys which has a given option:
    
    For example:
    g_dec_by_opt(<rules>,'level')
    can return:
    {'chapter', 'section', 'paragraph', 'stars', 'part', 'book'}
    '''
    s = set(rules.keys())
    d = set()      
    for e in s:
        if rules[e]['options'].get(option,None):
            d.add(e)
    return d

def hierarchy(rawstruct, rules, option='level'):
    '''Returns the sorted tuple of declarations of rawstruct
    based on a given option ('level' by defualt.)'''
    # You want the intersection of the available declaration keys, and the ones
    # in rawstruct. Plus you want to include option values of them in a
    # dictionary.
    l = g_dec_by_opt(rules,option) & s_rules(rawstruct)
    d={}
    for i in l:
        d[i] = rules[i]['options'][option]
    # Now you return the sorted tuple sorting based on values
    return tuple(sorted(d, key=d.get))



# map(str, list_of_ints)
#===============================================================================
# temporary
#===============================================================================

########## This goes to some verifying function
#   def options(declaration, rules):
#       return list(rules['declaration']['options'].keys())
#   def option(declaration, option):
#       return declaration.get('option', False)

def sub(rawstruct, rules, lineofdeclaration):
    rule = hierarchy(rawstruct,rules)
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
    hier = hierarchy(rawstruct,rules)
    if not depth:
        depth=len(hier)
    for line in l_lines(rawstruct):
        if rawstruct[line]['key'] in hier[0:depth]:
            print('    '*hier.index(rawstruct[line]['key'])+rawstruct[line]['key'])
    return None