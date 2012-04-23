import glob
import os
import re
import operator

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

def language(inputdata, declarationspath):
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

def declarations(inputdata, declarationspath):
    ''' Returns the declarations dictionary for inputdata'''
    # You want this function to return the dictionary for the document language
    # only.
    return declarations_dictionary(declarationspath)[language(inputdata, declarationspath)]

def dec_opt(rules,option):
    '''Returns the set of all the declaration keys which has a
    given option:
    
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

def struct(rawdata, rules, dictionary):
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
        # Now you want to define a list for your struct elements.
        rawstruct = {}
        # Now you want to get the locations of all the newlines of rawdata and
        # parse them one-by-one if they contain a declaration.
        locnewlines = gnparser.locnewlines(rawdata)
        for line in locnewlines:
            if rawdata[locnewlines[line]] == '{':
                # You want to add all the data gnparser could get of the
                # declaration itself...
                rawstruct[line] = decparser(gnparser.line(line, rawdata), rules, dictionary)
        return rawstruct
    
    def declines(rawstruct):
        '''Returns a sorted list of the line numbers of declarations.
        Useful to iterate elements of rawstruct.'''
        return sorted(list(rawstruct.keys()))
    
    def ind(line, dec_lines):
        '''Returns the index of a declaration by line'''
        if line in dec_lines:
            return dec_lines.index(line)
    
    def nextdecind(rawstruct, startline, key=None):
        '''Returns the index of the next declaration of a given key (any if None)'''
        _lines = declines(rawstruct)
        i = _lines.index(startline)
        for line in _lines[i+1:]:
            if not key or key == rawstruct[line]['key']:
                return ind(line,_lines)
            
    def decs(rawstruct, key):
        '''Returns the tuple of linenumbers starting with declaration
        of the given key.'''
        _lines = declines(rawstruct)
        l = []
        for line in _lines:
            if key == rawstruct[line]['key']:
                l.append(line)
        return tuple(l) 
    
    def hierarchy(rawstruct, rules, option='level'):
        '''Returns the sorted tuple of declarations of rawstruct
        based on a given option ('level' by defualt.)'''
        def s_rules(rawstruct):
            '''Returns a set of all different declaration keys of rawstruct.'''
            s = set()
            for line in declines(rawstruct):
                s.add(rawstruct[line]['key'])
            return s
        # You want the intersection of the available declaration keys, and the ones
        # in rawstruct. Plus you want to include option values of them in a
        # dictionary.
        l = dec_opt(rules,option) & s_rules(rawstruct)
        d={}
        for i in l:
            d[i] = rules[i]['options'][option]
        # Now you return the sorted tuple sorting based on values
        return tuple(sorted(d, key=d.get))
    # Now you want to create the structure data. Lets start some veriables to
    # make code easier and faster to compute:
    struct = []
    _rawstruct = rawstruct(rawdata, rules, dictionary)
    _lines = declines(_rawstruct)
    _hierarchy = hierarchy(_rawstruct, rules)
    # Now you want to start parsing all the declarations one by one:
    for line in _lines:
        # Again, some variables
        _dec = _rawstruct[line]['key']
        _decs = decs(_rawstruct, _dec)
        # First you want to add data from rawdata
        struct.append(_rawstruct[line])
        # Now the corresponding line number in the rawdata
        struct[-1].update(line=line)
        # The index of the next declaration
        struct[-1].update(nextany=nextdecind(_rawstruct, line))
        # The index of the next declaration which has the same key
        struct[-1].update(nextsame=nextdecind(_rawstruct, line, key=_dec))
        # Now the index of the current declaration among all declaratons with
        # same key.
        struct[-1].update(decindex=(_decs.index(line)))
        # Now the level if possible. To get this, the program will check which
        # body levels exists, sorts them, and returns the index of the current
        # declaration in that hierarchy.
        if _dec in _hierarchy:
            struct[-1].update(level=_hierarchy.index(_dec))
    return tuple(struct)

def deccounts(struct, rules):
    '''Returns the count of declarations in a dictionary.'''
    def counter(struct, key):
        '''Counts the occassions of a declaration in struct by key.'''
        n = 0
        for i in range(len(struct)):
            if key == struct[i]['key']:
                n += 1
        return n
    d={}
    for key in rules.keys():
        if counter(struct,key) > 0:
            d[key] = counter(struct,key)
    return d

def dec_ind(struct, key, name):
    '''Returns the first occassion of a given key in struct.'''
    for i in range(len(struct)):
        if key == struct[i]['key']:
            return struct[i].get(name,None)