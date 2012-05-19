import re

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
