import re

import gntools
import gp

from opts import declarations, decpath

def raw(inputdata, pr=True):
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
    _raw = re.sub('^\ufeff',r'',inputdata)
    # Now you want to make sure all current declaration is followed by an
    # empty line. This is necessary before you can continue.
    _raw = re.sub('}\n(?!\n)',r'}\n\n',_raw)
    _raw = re.sub('\n+{',r'\n\n{',_raw)
    
    _rawlen = len(_raw)

    with open(declarations, encoding='utf-8') as a_file:
        _rules = gp.rules(a_file.read())
    _dictionary = gp.declarations(_raw, decpath)
    _locnewlines = gntools.locnewlines(inputdata)
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

        _key = gp.layout.declaration_parser(_raw[loc0:loc1], _rules, _dictionary)['key']
        row = _rules[_key]['options'].get('row',False)
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

def utf(inputdata):
    '''Replaces parts (characters) of inputdata to their utf representative.'''
    # You want to replace dashes:
    inputdata = inputdata.replace('---','—') # Em dash
    inputdata = inputdata.replace('--','–') # Then en dash
    # You define a function to convert full quotes such {Q Lorem ipsum} to “Lorem
    # ipsum”. You call the function immediately.
    def conv_fullquote(inputdata):
        p = re.compile(r'"(.+?)"')
        r = re.sub(p, r'“\1”', inputdata)
        return r
    inputdata = conv_fullquote(inputdata)
    # Now you want the remaining "s to be converted to “s.
    inputdata = re.sub(r'"', r'“', inputdata)
    # Now you want to convert other quotemarks:
    inputdata = inputdata.replace(',,','„')
    inputdata = inputdata.replace("''","”")
    
    return inputdata