import glob
import os
import re
import operator

import gnparser

def rules(propdata):
    '''Parses rules from a rules file'''
    def raw():
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
    propkeys = list(raw().keys())
    for k in propkeys:
        prop[k] = {}
        # You want to work with the parts of rawdata, so you get them.
        propformat = raw()[k]['format']
        propoptions = raw()[k]['options']
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

def declarations_dictionary(decpath):
    ''' Creates the dictionary of declarations based on files in <gp.py_path>/data/languages/declarations/'''
    # You want to create a dictionary for upcoming data.
    dictionary = {}
    # Now you would like to get data from all declarations file of all
    # languages, so get their path one-by-one.
    for dict_file in glob.glob(decpath):
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

def declarations(inputdata, decpath):
    ''' Returns the declarations dictionary for inputdata'''
    # You want this function to return the dictionary for the document language
    # only.
    return declarations_dictionary(decpath)[language(inputdata, decpath)]