'''
Created on Apr 2, 2012

@author: adam szieberth

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
'''

import os
import glob
import re
import unicodedata
import sys
from optparse import OptionParser
from shutil import copy

parser = OptionParser()
parser.add_option('-f', '--file', action='store', type='string', dest='filename')
(options, args) = parser.parse_args()

gp_path=os.path.abspath(os.path.split(sys.argv[0])[0])
file_path=os.path.split(options.filename)[0]
file_name=os.path.split(options.filename)[1]
mode='kindle'



# Code: http://stackoverflow.com/questions/273192/python-best-way-to-create-directory-if-it-doesnt-exist-for-file-write
def ensure_dir(f):
    ''' Creates directory for output file if not exits
    
    If the input file is on the desktop, the output files will be located in ~/Desktop/kindle
    '''
    if not os.path.exists(f):
        os.makedirs(f)

def out_path():
    ''' Returns the path of output directory '''
    path = file_path+'/'+mode
    ensure_dir(path)
    return path

structs = ('part', 'chapter', 'intro', 'foreword')
depth = {'part': 1, 'chapter': 2, 'intro': 0, 'foreword': 'foreword'}


# Code:  http://stackoverflow.com/a/7829658
import hashlib
from functools import partial

def md5sum(filename):
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
    return d.hexdigest()

####

def raw():
    ''' Converts the structure of the sourcedata to a more comfortable one.'''
    # You want to open the sourcedata and name it
    with open(options.filename, encoding='utf-8') as a_file:
        raw = a_file.read()
        # Now we want to remove the zero width no-break space character at
        # the beginning of our data.
        raw = re.sub('^\ufeff',r'',raw)
        # Now you want to convert multilined declarations to a single line with
        # linebreaks. You want to make a function which replaces linebreaks to
        # '\\'s in your match.
        def singlelineize(match):
            inputdata = match.group()
            p = re.compile(r'\n')
            return p.sub(r'\\\\',inputdata)
        # Now you search for declarations, and singlelineize them.
        p = re.compile(r'^{.+?}', re.M|re.S)
        raw = p.sub(singlelineize, raw)
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

def utfize(inputdata):
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

def get_declarations(inputdata):
    ''' Returns the declarations dictionary for inputdata'''
    def declarations_dictionary():
        ''' Creates the dictionary of declarations based on files in <gp.py_path>/data/languages/declarations/'''
        # You want to create a dictionary for upcoming data.
        dictionary = {}
        # Now you would like to get data from all declarations file of all
        # languages, so get their path one-by-one.
        for dict_file in glob.glob(gp_path+'/data/languages/declarations/*'):
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
    def get_language(inputdata):
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
        for k in list(declarations_dictionary().keys()):
            # If the very first declaration is the actual key, you are done.
            # This works for '{HU}' kind language declaration.  
            if s.group('key').lower() == k:
                return k
            # Else you want to check all the keys of the actual language for
            # matching. 
            else:
                for l in list(declarations_dictionary()[k].keys()):
                    if s.group('key') == l:
                        # Now you only want allow 'k' to be the language if
                        # the respectable value in the dictionary is 'author'
                        # or 'title'.
                        if declarations_dictionary()[k][l] == 'author' or declarations_dictionary()[k][l] == 'title':
                            return k
    # You want this function to return the dictionary for the document language
    # only.
    
    return declarations_dictionary()[get_language(inputdata)]

def get_declaration_properties():
    def get_rawdata():
        d = {}
        with open(gp_path+'/data/declarations', encoding='utf-8') as a_file:
            file = a_file.read()
            s1 = True
            i = 0
            while s1:
                p1 = re.compile(r'^(?!#)(?P<declaration>.+?)\s{0,}:\s{0,}\((?P<format>.{0,}?)\)(?P<options>.{0,}?)$', flags=re.M)
                s1 = p1.search(file[i:])
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
        while s and propoptions:
            p = re.compile(r'\b(.+?)\b')
            s = p.search(propoptions[i:])
            if s:
                prop[k][s.group(1)] = True
                i += s.end()
        
    
    
    return prop

def d(inputdata):
    d = {}
    p1 = re.compile(r'{.+?}')
    m1 = p1.search(inputdata)
    if m1:
        p2 = re.compile(r'{(?P<key>.+?)\s|}')
        m2 = p2.search(m1.group())
        m1i = m2.end()
        p3 = re.compile(r'\s{0,}(?P<value>.+?)\s{0,}::')
        m3 = p3.search(m1.group()[m1i:])
        d['key'] = m2.group('key')
        
    return d

def get_linestarts(inputdata):
    linestarts = {}
    p = re.compile(r'^', re.M)
    s = p.finditer(inputdata)
    i = 1
    for m in s:
        linestarts[i] = m.span()[0]
        i += 1
#        print(m.span()[0])
    return linestarts

def get_line_nr(x, inputdata):
    linestarts = get_linestarts(inputdata)
    for l in range(2,len(linestarts)):
        if linestarts[l-1] <= x and linestarts[l] > x:
            return l-1
        elif linestarts[l] <= x and len(inputdata) > x:
            return l
        
def get_line(line, inputdata):
    linestarts = get_linestarts(inputdata)  
    return inputdata[linestarts[line]:linestarts.get(line+1, len(data)+1)-1]
    
        


def get_meta(inputdata):
    ''' Get metadata from modified gneposis data file '''
    reqdeclarations = ('author', 'title')
    optdeclarations = ('copyright', 'date', 'description', 'isbn')
    multipleentries = ('author')
    def get_required(inputdata):
        ''' Get required metadata using the reqdeclarations tuple
        
        An author declaration must look like:
        {<AUTHOR> <name> :: <sort_name>}
        
        For example (by language):
        en: {AUTHOR Jane Austen :: Austen, Jane}
        en: {AUTHOR Carlos Castañeda :: Castañeda, Carlos}
        hu: {SZERZŐ Gárdonyi Géza :: Gárdonyi, Géza}
        
        A title (and the optional subtitle) declaration must look like:
        {<TITLE> <title>[ :: <subtitle>]}
        
        For example (by language):
        en {TITLE Pride and Prejudice}
        en {TITLE Journey to Ixtlan :: The Lessons of Don Juan}
        hu {CÍM Egri csillagok}
        '''
        for s in reqdeclarations:
            p1 = re.compile(r'{'+dictionary()[language(inputdata)][s]+' (?P<_'+s+'_>.+?)}', re.S)
            m1 = p1.search(inputdata)
            if m1:
                p2 = re.compile(r'(?P<'+s+'>.+?)\s::\s(?P<'+s+'_2>.+?)$')
                m2 = p2.search(m1.group('_'+s+'_'))
                if m2:
                    d[s]=m2.group(s)
                    d[s+'_2']=m2.group(s+'_2')
                else:
                    d[s]=m1.group('_'+s+'_')
            else:
                raise Warning('Missing statement: '+s)
        return d
    def get_optional(inputdata):
        ''' Get optional metadata using the optdeclarations tuple
        
        The copyright statement is for the contents of the copyright page.
        You can use \\ to make linebreaks inside. Watch the "}" at the end of the
        declaration:
        {COPYRIGHT Lorem ipsum dolor sit amet, \\
        consectetur adipisicing elit, sed do eiusmod \\
        \\
        tempor incididunt ut labore et dolore magna aliqua. \\
        \\
        Ut enim \\
        ad minim veniam, quis nostrud exercitation ullamco \\ 
        \\
        laboris nisi ut aliquip ex ea commodo consequat.}
        
        Another declarations:
        {DATE 1966}
        {DESCRIPTION Lorem ipsum dolor sit amet, consectetur
        adipisicing elit, sed do eiusmod tempor incididunt
        ut labore et dolore magna aliqua. Ut enim ad minim
        veniam, quis nostrud exercitation ullamco laboris
        nisi ut aliquip ex ea commodo consequat.}
        {ISBN 978-3-16-148410-0} or {ISBN 9783161484100}
        '''
        
        d = {}
        for s in optdeclarations:
            p1 = re.compile(r'{'+dictionary()[language(inputdata)][s]+' (?P<'+s+'>.+?)}', re.S)
            m1 = p1.search(inputdata)
            if m1:
                d[s] = m1.group(s)
        return d   
    meta=dict(list(get_required(inputdata).items()) + list(get_optional(inputdata).items()))
    meta['language']=language(inputdata)
    return meta

def struct(gp):
    struct = []
    for s in structs:
        searching = True
        i = 1
        o = 0
        while searching:
            p1 = re.compile('{'+dictionary()[metadata['language']][s]+' (?P<'+s+'>.+?)}')
            m1 = p1.search(gp[o:])
            if m1:
                p2 = re.compile(r'(?P<'+s+'title>.+?)\s::\s(?P<'+s+'subtitle>.+?)$')
                m2 = p2.search(m1.group(s))
                if m2:
                    struct.append((o+m1.start(), o+m1.end(),(depth[s], i), s, m2.group(s+'title'), m2.group(s+'subtitle')))
                else:
                    struct.append((o+m1.start(), o+m1.end(),(depth[s], i), s, m1.group(s), None))
                i += 1
                o += m1.end()
            else:
                searching = False
    return sorted(struct)

def footnotes(gp):
    footnotes = []
    searching = True
    i = 1
    o = 0
    while searching:
        p = re.compile('{'+dictionary()[metadata['language']]['footnote']+' (?P<footnote>.+?)}')
        m = p.search(gp[o:])
        if m:
            footnotes.append((o+m.start(), o+m.end(), i, m.group('footnote')))
            i += 1
            o += m.end()
        else: 
            searching = False
    return footnotes

def get_re_string(input_string):
    string = input_string
    string = string.replace('\\','\\\\')
    string = string.replace('.','\.')
    string = string.replace('^','\^')
    string = string.replace('$','\$')
    string = string.replace('*','\*')
    string = string.replace('+','\+')
    string = string.replace('?','\?')
    string = string.replace('{','\{')
    string = string.replace('}','\}')
    string = string.replace('[','\[')
    string = string.replace(']','\]')
    string = string.replace('|','\|')
    string = string.replace('(','\(')
    string = string.replace(')','\)')
    return string

# Code:  http://code.activestate.com/recipes/576648-remove-diatrical-marks-including-accents-from-stri/
def remove_diacritic(i):
    '''
    Accept a unicode string, and return a normal string (bytes in Python 3)
    without any diacritical marks.
    '''
    return unicodedata.normalize('NFKD', i).encode('ASCII', 'ignore').decode()

def tocname(tocelement):
    tocname = None
    try:
        check = tocelement[2][0] >= 0
    except:
        check = False
    if check:
        if tocelement[2][0] < 2:
            if tocelement[5]:
                tocname = tocelement[4]+': '+tocelement[5]
            else:
                tocname = tocelement[4]
        else:
            if tocelement[5]:
                tocname = str(tocelement[2][1])+'. '+tocelement[5]
            else:
                tocname = str(tocelement[2][1])+'. '+tocelement[4]
    return tocname

saved_footnotes_kindle_html = []

def kindle_html(gp):
    def remove_meta(gp):
        metas = ('author', 'title', 'copyright', 'date', 'description', 'isbn')
        r = gp
        for m in metas:
            p = re.compile(r'{'+get_re_string(dictionary()[metadata['language']][m])+' (.+?)}\n', re.S)
            r = re.sub(p, r'', r)
        print('DONE')
        return r
    def add_header(gp):
        with open(gp_path+'/data/kindle/default/html_body_header', 'r', encoding='utf-8') as a_header:
            header = a_header.read()+'\n'
        p = re.compile(r'AUTHOR: TITLE')
        r = p.sub(metadata['author']+': '+metadata['title'],header)
        print('DONE')
        return r + gp
    def add_toc(gp):
        n = len(mainstruct)
        header = '<a name="toc"><div class="toc">'+dictionary()[metadata['language']]['Toc']+'</div></a>\n'
        body = ''
        for s in range(n):
            try:
                check = mainstruct[n-s-1][2][0] >= 0
            except:
                check = False
            if check:
                body = '<div class="toclvl'+str(mainstruct[n-s-1][2][0])+'"><a href="#'+str(mainstruct[n-s-1][2][0])+'-'+str(mainstruct[n-s-1][2][1])+'">'+tocname(mainstruct[n-s-1])+'</a></div>\n'+body
        print('DONE')
        return header + body + gp
    def add_titlepage(gp):
        page = '<a name="start"/>\n<div class="author">'+metadata['author']+'</div>\n'+'<div class="title">'+metadata['title']+'</div>\n'
        try:
            check = metadata['title_2']
        except:
            check = False
        if check:
            page = page+'<div class="subtitle">'+metadata['title_2']+'</div>\n'
        page=page+'<div style="page-break-after:always; margin-top: 2%"></div>\n'
        print('DONE')
        return page + gp
    def add_copyrightpage(gp):
        page = '<div class="copyright">'+metadata['copyright']+'</div>\n'
        print('DONE')
        return page + gp
    def conv_br(gp):
        p = re.compile(r'\s{0,}?\\\\')
        r = re.sub(p, r'<br/>', gp)
        print('DONE')
        return r
    def conv_emph(gp):
        #   def conv_emph(gp):
#       p = re.compile(r'_(.+?)_')
#       r = re.sub(p, r'<i>\1</i>', gp)
#       return r
        p = re.compile(r'_(.+?)_')
        r = re.sub(p, r'<i>\1</i>', gp)
        print('DONE')
        return r
    def conv_p(gp):
        p1 = re.compile(r'\n\n(?!{)')
        r1 = re.sub(p1, r'\n<p>', gp)
        p2 = re.compile(r'^<p>(.+?)$', re.M)
        r2 = re.sub(p2, r'<p>\1</p>', r1)
        print('DONE')
        return r2
    def conv_paragraph(gp):
        p = re.compile(r'{'+dictionary()[metadata['language']]['paragraph']+' (.+?)}')
        r = re.sub(p, r'<p class="paragraph">\1</p>', gp)
        print('DONE')
        return r
    def conv_right(gp):
        p = re.compile(r'{'+dictionary()[metadata['language']]['right']+' (.+?)}')
        r = re.sub(p, r'<div align="right">\1</div>', gp)
        print('DONE')
        return r
    def conv_footnotes(gp):
        global saved_footnotes_kindle_html
        saved_footnotes_kindle_html = footnotes(gp)
        r = gp
        for f in range(len(footnotes(gp))):
            p = re.compile('{'+dictionary()[metadata['language']]['footnote']+' '+get_re_string(footnotes(gp)[f][3])+'}')
            r = p.sub('<a name="fn_name_'+str(footnotes(gp)[f][2])+'" href="#fn_index_'+str(footnotes(gp)[f][2])+'"><span class="footnote"><sup>'+str(footnotes(gp)[f][2])+'</sup></span></a>',r)
        print('DONE')
        return r
    def add_footnotes(gp):
        gp = gp + '\n\n<a name="footnotes"><div class="footnotes">'+dictionary()[metadata['language']]['Notes']+':</div></a>\n'
        for f in range(len(saved_footnotes_kindle_html)):
            footnote = '<div class="footnoteitem">[<a name="fn_index_'+str(saved_footnotes_kindle_html[f][2])+'" href="#fn_name_'+str(saved_footnotes_kindle_html[f][2])+'">'+str(saved_footnotes_kindle_html[f][2])+'</a>] '+saved_footnotes_kindle_html[f][3]+'</div>\n'
            gp = gp + footnote
        print('DONE')
        return gp
    def add_footer(gp):
        gp = gp + '\n</body>\n</html>'
        print('DONE')
        return gp
    def conv_struct(gp):
        r = gp
        for s in range(len(mainstruct)):
            if mainstruct[s][5] is None:
                p = re.compile('{'+dictionary()[metadata['language']][mainstruct[s][3]]+' '+get_re_string(mainstruct[s][4])+'}')
                r = p.sub('<a name="'+str(mainstruct[s][2][0])+'-'+str(mainstruct[s][2][1])+'"><div class="'+mainstruct[s][3]+'_alone">'+mainstruct[s][4]+'</div></a>',r)
            else:
                p = re.compile('{'+dictionary()[metadata['language']][mainstruct[s][3]]+' '+get_re_string(mainstruct[s][4])+' :: '+get_re_string(mainstruct[s][5])+'}')
                r = p.sub('<a name="'+str(mainstruct[s][2][0])+'-'+str(mainstruct[s][2][1])+'"><div class="'+mainstruct[s][3]+'_withtitle">'+mainstruct[s][4]+'</div></a>\n<div class="'+mainstruct[s][3]+'title">'+mainstruct[s][5]+'</div>',r)
        print('DONE')
        return r
    def conv_announcement(gp):
        p1 = re.compile(r'{'+dictionary()[metadata['language']]['announcement']+' (.+?)}')
        r1 = re.sub(p1, r'<div class="announcementtitle">\1</div>', gp)
        p2 = re.compile(r'{'+dictionary()[metadata['language']]['announcement']+' (.+?)}')
        r2 = re.sub(p2, r'<div class="announcementtitle">\1</div>', r1)
        print('DONE')
        return r2
    def conv_verse(gp):
        p = re.compile(r'{'+dictionary()[metadata['language']]['verse']+' (.+?)}', re.S)
        r = re.sub(p, r'<div class="verse">\1</div>', gp)
        print('DONE')
        return r
    print('\nGenerating Kindle compatible HTML file:')
    print('-'*80)
    print('    Remove metadata... ', end='')
    gp = remove_meta(gp)
    print('    Convert emphasized parts... ', end='')
    gp = conv_emph(gp)
    print('    Convert paragraphs... ', end='')
    gp = conv_p(gp)
    print('    Generating TOC... ', end='')
    gp = add_toc(gp)
    print('    Add copyright page... ', end='')
    gp = add_copyrightpage(gp)
    print('    Add titlepage... ', end='')
    gp = add_titlepage(gp)
    print('    Generating header... ', end='')
    gp = add_header(gp)
    print('    Convert right indented blocks... ', end='')
    gp = conv_right(gp)
    print('    Convert paragraph titles... ', end='')
    gp = conv_paragraph(gp)
    print('    Convert inline footnotes... ', end='')
    gp = conv_footnotes(gp)
    print('    Generating footnotes... ', end='')
    gp = add_footnotes(gp)
    print('    Convert text parts... ', end='')
    gp = conv_struct(gp)
    print('    Convert announcements... ', end='')
    gp = conv_announcement(gp)
    print('    Convert verse... ', end='')
    gp = conv_verse(gp)
    print('    Convert linebreaks... ', end='')
    gp = conv_br(gp)
    print('    Generating footer... ', end='')
    gp = add_footer(gp)
    return gp

def kindle_ncx():
    def add_header():
        with open(gp_path+'/data/kindle/default/ncx_header', 'r', encoding='utf-8') as a_header:
            header = a_header.read()+'\n'
        p = re.compile(r'xml:lang="unknown"')
        r = p.sub('xml:lang="'+metadata['language']+'"',header)
        print('DONE')
        return r
    def add_head():
        head = '<head>\n<meta name="dtb:uid" content="'+metadata['hash']+'"/> <!-- same as in .opf -->\n<meta name="dtb:depth" content="1"/> <!-- 1 or higher -->\n<meta name="dtb:totalPageCount" content="0"/> <!-- must be 0 -->\n<meta name="dtb:maxPageNumber" content="0"/> <!-- must be 0 -->\n</head>'
        print('DONE')
        return head
    def add_doctitle_docauthor():
        content = '\n<docTitle>\n<text>'+metadata['title']+'</text>\n</docTitle>'+'\n<docAuthor>\n<text>'+metadata['author']+'</text>\n</docAuthor>'
        print('DONE')
        return content
    def add_navmap():
        def add_navpoint():
            content = ''
            n = len(mainstruct)
            i = 1
            for s in range(n):
                try:
                    check = mainstruct[s][2][0] >= 0
                except:
                    check = False
                if check:
                    nav_id = str(mainstruct[s][2][0])+'-'+str(mainstruct[s][2][1])
                    content = content+'\n<navPoint class="'+mainstruct[s][3]+'" id="'+nav_id+'" playOrder="'+str(i)+'">\n<navLabel><text>'+tocname(mainstruct[s])+'</text></navLabel>\n<content src=body.html#'+nav_id+' />\n</navPoint>'
                    i += 1      
            return content
        content = '\n<navMap>'+add_navpoint()+'\n</navMap>\n</ncx>'
        print('DONE')                                                                                
        return content
    print('\nGenerating Kindle compatible TOC.ncx file:')
    print('-'*80)
    print('    Generating header... ', end='')
    ncx = add_header()
    print('    Generating <head>... ', end='')
    ncx = ncx+add_head()
    print('    Generating <docTitle>,<docAuthor>... ', end='')
    ncx = ncx+add_doctitle_docauthor()
    print('    Generating <navMap>... ', end='')
    ncx = ncx+add_navmap()
    return ncx

def kindle_opf():
    def add_header():
        with open(gp_path+'/data/kindle/default/opf_header', 'r', encoding='utf-8') as a_header:
            header = a_header.read()
        package = '<package unique-identifier="'+metadata['hash']+'">'
        print('DONE')
        return header+package+'\n'
    def add_metadata():
        def add_header():
            with open(gp_path+'/data/kindle/default/opf_metadata_header', 'r', encoding='utf-8') as a_header:
                header = '<metadata>\n'+a_header.read()
            return header
        def add_common_metadata(meta):
            content = ''
            try:
                check = metadata[meta]
            except:
                check = False
            if check:
                content = '<dc:'+meta.capitalize()+'>'+metadata[meta]+'</dc:'+meta.capitalize()+'>\n'
            return content
        def add_author():
            content = '<dc:Creator opf:file-as="'+remove_diacritic(metadata['author_2'])+'" opf:role="aut">'+metadata['author']+'</dc:Creator>'
            return content+'\n'
        def add_identifier():
            content = '<dc:Identifier id="uid">'+metadata['hash']+'</dc:Identifier>\n'
            try:
                check = metadata['isbn']
            except:
                check = False
            if check:
                content = content+'<dc:Identifier opf:scheme="ISBN">'+metadata['isbn']+'</dc:Identifier>\n'
            return content
        def add_footer():
            content='''</dc-metadata>
<x-metadata>
<EmbeddedCover>cover.jpg</EmbeddedCover>
<output encoding="utf-8"></output>
</x-metadata>
<meta name="cover" content="my-cover-image" />
</metadata>
'''
            return content
        metadata = add_header()
        metadata = metadata + add_common_metadata('title')
        metadata = metadata + add_common_metadata('language')
        metadata = metadata + add_author()
        metadata = metadata + add_common_metadata('date')
        metadata = metadata + add_common_metadata('description')
        metadata = metadata + add_identifier()
        metadata = metadata + add_footer()
        print('DONE')
        return metadata
    def add_manifest():
        def add_cover():
            content = '<item id="my-cover-image" media-type="image/jpeg" href="cover.jpg"/>\n'
            return content
        def add_tocncx():
            content = '<item id="toc" media-type="application/x-dtbncx+xml" href="toc.ncx"/>\n'
            return content
        def add_html(htmlname):
            content = '<item id="'+htmlname+'" media-type="text/x-oeb1-document" href="'+htmlname+'.html"/>\n'
            return content
        body = add_cover()+add_tocncx()+add_html('body')
        print('DONE')
        return '<manifest>\n'+body+'</manifest>\n'
    def add_spine():
        body = '<itemref idref="body"/>\n'
        print('DONE')
        return '<spine toc="toc">\n'+body+'</spine>\n'
    def add_guide():
        start = '<reference type="start" title="Go to Beginning" href="body.html#start"/>\n'
        toc = '<reference type="toc" title="Table of Contents" href="body.html#toc"/>\n'
        print('DONE')
        return '<guide>\n'+start+toc+'</guide>\n'

    print('\nGenerating Kindle compatible .opf file:')
    print('-'*80)
    print('    Generating header... ', end='')
    opf = add_header()
    print('    Generating metadata... ', end='')
    opf = opf+add_metadata()
    print('    Generating manifest... ', end='')
    opf = opf+add_manifest()
    print('    Generating spine... ', end='')
    opf = opf+add_spine()
    print('    Generating guide... ', end='')
    opf = opf+add_guide()
    return opf+'</package>'

def kindle_copy():
    print('\nCopying necessary files:')
    print('-'*80)
    print('    Copying .css file... ', end='')
    copy(gp_path+'/data/kindle/default/default.css',out_path())
    print('DONE')
    print('    Copying cover.jpg file... ', end='')
    copy(file_path+'/cover.jpg',out_path())
    print('DONE')

if __name__ == '__main__':
#    pass
    print('gneposis-publisher 0.1alpha by Adam Szieberth')
    print('='*80)
    
    data = utfize(raw())
    declarations = get_declarations(data)
#    metadata = get_meta(data)
    
    
#   metadata = meta(data)
#   metadata['hash'] = md5sum(options.filename)
#   mainstruct = struct(data)
#   mainfootnotes = footnotes(data)
#
#   with open(out_path()+'/body.html', 'w', encoding='utf-8') as a_body:
#       a_body.write(kindle_html(data))
#
#   with open(out_path()+'/toc.ncx', 'w', encoding='utf-8') as a_ncx:
#       a_ncx.write(kindle_ncx())
#   
#   with open(out_path()+'/body.opf', 'w', encoding='utf-8') as a_opf:
#       a_opf.write(kindle_opf())
#       
#   kindle_copy()
    
    with open(file_path+'/'+file_name.split('.')[0]+'.raw', 'w', encoding='utf-8') as a_raw:
        a_raw.write(data)
        
    a = get_declaration_properties()