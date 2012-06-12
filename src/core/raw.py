import re

from gntools.reformat import trim
import core.dictionary
import core.opts
import core.rules


def statement_parser(s, rules=core.rules.make(), dictionary=core.dictionary.make(core.opts.dec_path)):
    '''Parses a statement string'''
    common_statements = {'{': 'left_curly',
                         '}': 'right_curly',
                         '_': 'underscore',
                         '/': 'end',
                         '***': 'stars'}
    s1 = s[1:-1]
    if s1 in common_statements:
        key = common_statements[s1]
    else:
        key = dictionary[s1.split()[0]]
    s2 = ' '.join(s1.split()[1:])
    args = [ trim(i) for i in s2.split('::') ]
    return key, tuple(args)

def get_statement(s, st=0):
        start = s.find('{', st)
        if start < 0:
            return None
        end = start + 3 + s[start+2:].find('}')
        return start, end

def get_raw(data, rules=core.rules.make(), dictionary=core.dictionary.make(core.opts.dec_path)):
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
    # You want to remove the zero width no-break space character at
    # the beginning of your inputdata.
    _raw = re.sub('^\ufeff',r'',data)
    # Now you want to make sure all current declaration is followed by an
    # empty line. This is necessary before you can continue.
    _raw = re.sub('}\n(?!\n)',r'}\n\n',_raw)
    _raw = re.sub('\n+{',r'\n\n{',_raw)
    
    _rawlen = len(_raw)
    
    loc1 = 0
    next_statement = True
    raw = ''
    row = False
    while next_statement:
        loc0 = loc1
        next_statement = get_statement(_raw[loc0:])
        if not next_statement:
            loc1 = _rawlen
        else:
            second_next_statement = get_statement(_raw[loc0 + next_statement[1]:])
            _key = statement_parser(_raw[loc0 + next_statement[0] : loc0 + next_statement[1]])[0]
            row = rules[_key]['options'].get('row',False)
            if not second_next_statement:
                loc1 = _rawlen
            else:
                loc1 = loc0 + next_statement[1] + second_next_statement[0]
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

    return raw

def make(save=True):
    with open(core.opts.file, encoding='utf-8') as a_file:
        raw = get_raw(a_file.read())
    if save:
        with open(core.opts.filepath+'/'+core.opts.filefile+'.raw.'+core.opts.fileext, 'w', encoding='utf-8') as a_raw:
            a_raw.write(raw)
    return raw