import re
from glob import glob
from os import path
from .declarat import parser
from core.pickler import load, save
from gntools.lines import content, newlines, nr

def get_dictionary(decpath, language):
    ''' Returns the declarations dictionary for inputdata'''
    # You want this function to return the dictionary for the document language
    # only.
    return get_full_dictionary(decpath)[language]

def get_full_dictionary(decpath):
    ''' Creates the dictionary of declarations based on files in <gp.py_path>/data/languages/declarations/'''
    # You want to create a dictionary for upcoming data.
    dictionary = {}
    # Now you would like to get data from all declarations file of all
    # languages, so get their path one-by-one.
    for dict_file in glob(decpath):
        # You need to split filename and get its language key.
        path_split = path.split(dict_file)
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

def get_language(data, decpath):
    ''' Gets language key from beginning of inputdata:
    
    If inputdata begins with '{hu}' or '{HU}' it returns 'hu' if there is a
    hu file in /data/languages/declarations/.
    
    If inputdata begins with '{AUTHOR ...}' or '{TITLE ...}' it returns
    'en' since it will find AUTHOR or TITLE as a valid author or title 
    declaration in the english declaration file. Same with '{SZERZŐ ...}'
    for hungarian; this returns 'hu'.
    '''
    # You want to search for the very first declaration of inputdata.
    s = re.search(r'^{(?P<key>.+?)\s|}', data)
    # Now you want to check all languages. 'k' returns their keys.
    for k in list(get_full_dictionary(decpath).keys()):
        # If the very first declaration is the actual key, you are done.
        # This works for '{HU}' kind language declaration.  
        if s.group('key').lower() == k:
            return k
        # Else you want to check all the keys of the actual language for
        # matching. 
        else:
            for l in list(get_full_dictionary(decpath)[k].keys()):
                if s.group('key') == l:
                    # Now you only want allow 'k' to be the language if
                    # the respectable value in the fulldictionary is 'author'
                    # or 'title'.
                    if get_full_dictionary(decpath)[k][l] == 'author' or get_full_dictionary(decpath)[k][l] == 'title':
                        return k

def get_layout(data, rules, dictionary, debug=False, pr=False):
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
        _newlines = newlines(data)
        find_loc = 0
        line = 1
        st = 0
        while find_loc>=0:
            find_loc = data[st:].find('{')
            if find_loc>=0:
                previousline = line
                line = nr(find_loc + st, data)
                st = _newlines[line]
                # Since it can be a long process, you want to put a progress
                # message.
                if pr == True:
                    print('\rGenerating layout: {0}/{1} ({2}%)'.format(line,len(_newlines),round(line/len(_newlines)*100,1)).ljust(61),end='')
                # You want to get the content of the current line
                c = content(line, data)
                # Now you want to search for anything between {}-s.
                p = re.compile(r'{.+?}')
                # Since there can be more match, you want them all. 'fi' will
                # return the list of them and you will get the column from it
                fi, it = p.findall(c), p.finditer(c)
                if fi:
                    i = 0
                    for e in it:
                        # Add the data parser can get, first.
                        layout.append(parser(fi[i], rules, dictionary))
                        # Now the current line number in data.
                        layout[-1].update(line=line)
                        # Now the start and end column of the match.
                        layout[-1].update(column=e.span())
                        # Now you want to add css names based on key. However,
                        # you want to know if a section comes immediately after
                        # a chapter, so you can handle the vertical spaces
                        # between those titles in the css file of your html.
                        _key = parser(fi[i], rules, dictionary)['key']
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
                        
                        i += 1
                        
            else:
                if pr == True:
                    print('\rGenerating layout: {0}/{0} (100%)'.format(len(_newlines)).ljust(61),end='')
        
        # You want to save the layout since it is a long process to get.
        # Moreover, future calls will be fast as hell...
        save(data, layout)
    if pr == True:
        print('[DONE]'.rjust(7))
    return tuple(layout)

def get_rules(data):
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
            s = p.search(data[i:])
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

def get_raw(data, rules, dictionary, pr=True):
    def trimnewline(content,newlinecount=2,replacestring='\\n'):
        r = True
        while r:
            p = re.compile(r'\n{'+str(newlinecount)+',}')
            # Now you look for a match in 'r'. It returns None if no more
            # empty lines exist, and the loop will also end.
            r = p.search(content)
            if r:
                content = p.sub(str(replacestring),content)
        return content
    def removebordernewlines(content):
        content = re.sub(r'\n+$',r'\n',content)
        content = re.sub(r'}\n{2,}',r'}\n',content)
        return content

    if pr == True:
        print('\rMaking raw file: Initial replaces'.ljust(61),end='')
    # You want to remove the zero width no-break space character at
    # the beginning of your inputdata.
    _raw = re.sub('^\ufeff',r'',data)
    # Now you want to make sure all current declaration is followed by an
    # empty line. This is necessary before you can continue.
    _raw = re.sub('}\n(?!\n)',r'}\n\n',_raw)
    _raw = re.sub('\n+{',r'\n\n{',_raw)
    
    _rawlen = len(_raw)
     
    loc_dec = 0
    loc1 = 0
    raw = ''
    row = False
    while loc_dec>=0:        
        loc0 = loc1
        
        if pr == True:
            print('\rMaking raw file: {0}/{1} ({2}%)'.format(loc0,_rawlen,round(loc0/_rawlen*100,1)).ljust(61),end='')
        
        loc_dec = _raw[loc0+1:].find('{')
        if loc_dec < 0:
            loc1 = None
        else:
            loc1 = loc0+loc_dec+1

        _key = parser(_raw[loc0:loc1], rules, dictionary)['key']
        row = rules[_key]['options'].get('row',False)
        content = _raw[loc0:loc1]

        if row == False:
            content = trimnewline(content,replacestring='@@@')
            content = re.sub(r'\n',r' ', content, flags=re.M)
            content = re.sub(r'@@@',r'\n', content, flags=re.M)
        else:
            content = trimnewline(content,newlinecount=3)
            content = removebordernewlines(content)
  
        raw = raw + content
        
        # To do this you search for a linebreak which is not followed by a "{".
        # After it comes all contains of that line till the end of the line,
        # which is grouped.
        # For replace you want the group (without the linebreak) followed by a
        # whitespace.
    
        # Now you need to trim the trailing whitespace(s) the source document
        # may had and the previous code made.
        raw = re.sub(r' +$',r'', raw, flags=re.M)
        # Now you want to get rid of whitespaces in a row. You use a loop
        # again, much like the one before.
        r = True
        while r:
            p = re.compile(r'  ')
            r = p.search(raw)
            if r:
                raw = p.sub(r' ',raw)
    
    if pr == True:
        print('\rMaking raw file: {0}/{0} (100%)'.format(_rawlen).ljust(61),end='')

    return raw