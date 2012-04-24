import re

def raw(inputdata):
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
    # To do this you search for a linebreak which is not followed by a "{".
    # After it comes all contains of that line till the end of the line,
    # which is grouped.
    # For replace you want the group (without the linebreak) followed by a
    # whitespace.
    raw = re.sub(r'\n(?!{)(.+)$',r'\1 ', raw, flags=re.M)
    # Now you need to trim the trailing whitespace(s) the source document
    # may had and the previous code made.
    raw = re.sub(r'\s+$',r'', raw, flags=re.M)
    # Now you want to get rid of remaining empty lines. You use a loop to
    # do the job until they exist.
    r = True
    while r:
        p = re.compile(r'\n\n')
        # Now you look for a match in 'r'. It returns None if no more
        # empty lines exist, and the loop will also end.
        r = p.search(raw)
        if r:
            raw = p.sub(r'\n',raw)
    # Now you want to get rid of whitespaces in a row. You use a loop
    # again, much like the one before.
    r = True
    while r:
        p = re.compile(r'\s\s')
        r = p.search(raw)
        if r:
            raw = p.sub(r' ',raw)        
    # Now you want to get rid of spaces around linebreak declarations
    # ('\\') you may have in your source document. They no need in your
    # rawdata.
    # You do it in two steps, one for starting, and one for trailing
    # whitespaces.
    raw = re.sub(r'\s\\\\',r'\\\\', raw)
    raw = re.sub(r'\\\\\s',r'\\\\', raw)

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