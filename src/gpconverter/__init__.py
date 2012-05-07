import re

import gnparser
import gp

from opts import declarations, decpath

def preraw(inputdata):
    ''' Converts the structure of the sourcedata to a more comfortable one.'''
    # You want to remove the zero width no-break space character at
    # the beginning of your inputdata.
    raw = re.sub('^\ufeff',r'',inputdata)
    # Now you want to make sure all current declaration is followed by an
    # empty line. This is necessary before you can continue.
    
    raw = re.sub('}\n(?!{|\n)',r'}\n\n',raw)
    
    # Now you want to make all the paragraphs to go in a single line and
    # all the declarations to have their own line. Plus you want no empty
    # lines to remain.
    # You also want to be able to switch between paragraph mode or row mode.
    # For that you want to parse the document line-by-line:
    return raw


def raw(inputdata):
    def trimnewline(content,newlinecount=2):
        r = True
        while r:
            p = re.compile(r'\n{'+str(newlinecount)+',}')
            # Now you look for a match in 'r'. It returns None if no more
            # empty lines exist, and the loop will also end.
            r = p.search(content)
            if r:
                content = p.sub(r'\n',content)
        return content
    def removebordernewlines(content):
        content = re.sub(r'\n+$',r'\n',content)
        content = re.sub(r'}\n{2,}',r'}\n',content)
        return content

    _raw = preraw(inputdata)
    with open(declarations, encoding='utf-8') as a_file:
        _rules = gp.decrules(a_file.read())
    _dictionary = gp.declarations(_raw, decpath)
    _locnewlines = gnparser.locnewlines(inputdata)
    loc_dec = 0
    loc1 = 0
    raw = ''
    row = False
    while loc_dec>=0:
        
        loc0 = loc1
        loc_dec = _raw[loc0+1:].find('{')
        if loc_dec < 0:
            loc1 = None
        else:
            loc1 = loc0+loc_dec+1
        
        _key = gp.layout.declaration_parser(_raw[loc0:loc1], _rules, _dictionary)['key']
        row = _rules[_key]['options'].get('row',False)
        
        print(loc0,loc_dec,loc1,_key,row)
        content = _raw[loc0:loc1]
        if row == False:
            # TODO: LÁBJEGYZET,,Jó estét!''
            content = re.sub(r'\n(?!{)(.+)$',r'\1 ', content, flags=re.M)
            content = trimnewline(content)
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