'''
Created on Apr 2, 2012

@author: adam szieberth
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


metas = ('title', 'subtitle', 'copyright', 'date', 'description', 'isbn')
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

def dictionary():
    dictionary = {}
    for dict_file in glob.glob('data/languages/*'):
        path_split = os.path.split(dict_file)
        lang = path_split[1]
        dictionary[lang] = {}
        line_number = 0
        with open(dict_file, encoding='utf-8') as a_file:
            for a_line in a_file:
                line_number += 1
                key = re.split('\W+?', a_line)[0]
                value = re.split('\W+?', a_line)[2]
                dictionary[lang][key] = value
    return dictionary

def language():
    with open(options.filename, encoding='utf-8') as a_file:
        a_file.seek(0)
        first_line = a_file.readline()
        key = re.split('\W+?', first_line)[1]
        for language in dictionary():
            if dictionary()[language]['author'] == key or dictionary()[language]['title'] == key:
                return language

def raw():
    with open(options.filename, encoding='utf-8') as a_file:
        raw = a_file.read()
        # deal with preamble
        raw = re.sub(r'}\n{', r'}\\\\\n{', raw)

        # \n\n to @@@ and \n to \s and back with @@@s
        raw = re.sub(r'\n\n', r'@@@', raw)
        raw = re.sub(r'\n', r' ', raw)
        raw = re.sub(r' $', r'', raw)
        raw = re.sub(r'@@@', r'\n\n', raw)
        
        # deal with linebreaks
        raw = re.sub(r'\\\\\s{0,}', r'\\\\\n', raw)
        
        # deal with preamble again
        raw = re.sub(r'}\\\\\n{', r'}\n{', raw)
    return raw

def utfize(gp):
    gp = gp.replace('--','–')
    gp = gp.replace(',,','„')
    gp = gp.replace("''","”")
    return gp

def meta(gp):
    def get_language():
        if language() == 'default':
            lang='en'
        else:
            lang=language()
        return lang
    def get_author():
        p1 = re.compile(r'{'+dictionary()[language()]['author']+' (?P<c>.+?)}', re.S)
        m1 = p1.search(gp)
        d = {}
        if m1:
            p2 = re.compile(r'(?P<author>.+?)\s::\s(?P<sortauthor>.+?)$')
            m2 = p2.search(m1.group('c'))
            d['author']=m2.group('author')
            d['sortauthor']=m2.group('sortauthor')
        return d
    meta = {}
    for m in metas:
        p = re.compile(r'{'+dictionary()[language()][m]+' (?P<'+m+'>.+?)}', re.S)
        s = p.search(gp)
        meta[m] = s.group(m)
    meta=dict(list(meta.items()) + list(get_author().items()))
    meta['language']=get_language()
    return meta

def struct(gp):
    struct = []
    for s in structs:
        searching = True
        i = 1
        o = 0
        while searching:
            p1 = re.compile('{'+dictionary()[language()][s]+' (?P<'+s+'>.+?)}')
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
        p = re.compile('{'+dictionary()[language()]['footnote']+' (?P<footnote>.+?)}')
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
        r = gp
        for m in metas:
            p = re.compile(r'{'+get_re_string(dictionary()[language()][m])+' (.+?)}\n', re.S)
            r = re.sub(p, r'', r)
        p2 = re.compile(r'{'+dictionary()[language()]['author']+' (.+?)}\n', re.S)
        r2 = re.sub(p2, r'', r)
        print('DONE')
        return r2
    def add_header(gp):
        with open('data/kindle/default/html_body_header', 'r', encoding='utf-8') as a_header:
            header = a_header.read()+'\n'
        p = re.compile(r'AUTHOR: TITLE')
        r = p.sub(mainmeta['author']+': '+mainmeta['title'],header)
        print('DONE')
        return r + gp
    def add_toc(gp):
        n = len(mainstruct)
        header = '<a name="toc"><div class="toc">'+dictionary()[language()]['Toc']+'</div></a>\n'
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
        page = '<a name="start"/>\n<div class="author">'+mainmeta['author']+'</div>\n'+'<div class="title">'+mainmeta['title']+'</div>\n'+'<div class="subtitle">'+mainmeta['subtitle']+'</div>\n'+'<div style="page-break-after:always; margin-top: 2%"></div>\n'
        print('DONE')
        return page + gp
    def add_copyrightpage(gp):
        page = '<div class="copyright">'+mainmeta['copyright']+'</div>\n'
        print('DONE')
        return page + gp
    def conv_br(gp):
        p = re.compile(r'\s{0,}?\\\\')
        r = re.sub(p, r'<br/>', gp)
        print('DONE')
        return r
    def conv_emph(gp):
        p = re.compile(r'{'+dictionary()[language()]['emph']+' (.+?)}')
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
        p = re.compile(r'{'+dictionary()[language()]['paragraph']+' (.+?)}')
        r = re.sub(p, r'<p class="paragraph">\1</p>', gp)
        print('DONE')
        return r
    def conv_right(gp):
        p = re.compile(r'{'+dictionary()[language()]['right']+' (.+?)}')
        r = re.sub(p, r'<div align="right">\1</div>', gp)
        print('DONE')
        return r
    def conv_footnotes(gp):
        global saved_footnotes_kindle_html
        saved_footnotes_kindle_html = footnotes(gp)
        r = gp
        for f in range(len(footnotes(gp))):
            p = re.compile('{'+dictionary()[language()]['footnote']+' '+get_re_string(footnotes(gp)[f][3])+'}')
            r = p.sub('<a name="fn_name_'+str(footnotes(gp)[f][2])+'" href="#fn_index_'+str(footnotes(gp)[f][2])+'"><span class="footnote"><sup>'+str(footnotes(gp)[f][2])+'</sup></span></a>',r)
        print('DONE')
        return r
    def add_footnotes(gp):
        gp = gp + '\n\n<a name="footnotes"><div class="footnotes">'+dictionary()[language()]['Notes']+':</div></a>\n'
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
                p = re.compile('{'+dictionary()[language()][mainstruct[s][3]]+' '+get_re_string(mainstruct[s][4])+'}')
                r = p.sub('<a name="'+str(mainstruct[s][2][0])+'-'+str(mainstruct[s][2][1])+'"><div class="'+mainstruct[s][3]+'_alone">'+mainstruct[s][4]+'</div></a>',r)
            else:
                p = re.compile('{'+dictionary()[language()][mainstruct[s][3]]+' '+get_re_string(mainstruct[s][4])+' :: '+get_re_string(mainstruct[s][5])+'}')
                r = p.sub('<a name="'+str(mainstruct[s][2][0])+'-'+str(mainstruct[s][2][1])+'"><div class="'+mainstruct[s][3]+'_withtitle">'+mainstruct[s][4]+'</div></a>\n<div class="'+mainstruct[s][3]+'title">'+mainstruct[s][5]+'</div>',r)
        print('DONE')
        return r
    def conv_announcement(gp):
        p1 = re.compile(r'{'+dictionary()[language()]['announcement']+' (.+?)}')
        r1 = re.sub(p1, r'<div class="announcementtitle">\1</div>', gp)
        p2 = re.compile(r'{'+dictionary()[language()]['announcement']+' (.+?)}')
        r2 = re.sub(p2, r'<div class="announcementtitle">\1</div>', r1)
        print('DONE')
        return r2
    def conv_verse(gp):
        p = re.compile(r'{'+dictionary()[language()]['verse']+' (.+?)}', re.S)
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
        with open('data/kindle/default/ncx_header', 'r', encoding='utf-8') as a_header:
            header = a_header.read()+'\n'
        p = re.compile(r'xml:lang="unknown"')
        r = p.sub('xml:lang="'+mainmeta['language']+'"',header)
        print('DONE')
        return r
    def add_head():
        head = '<head>\n<meta name="dtb:uid" content="'+mainmeta['hash']+'"/> <!-- same as in .opf -->\n<meta name="dtb:depth" content="1"/> <!-- 1 or higher -->\n<meta name="dtb:totalPageCount" content="0"/> <!-- must be 0 -->\n<meta name="dtb:maxPageNumber" content="0"/> <!-- must be 0 -->\n</head>'
        print('DONE')
        return head
    def add_doctitle_docauthor():
        content = '\n<docTitle>\n<text>'+mainmeta['title']+'</text>\n</docTitle>'+'\n<docAuthor>\n<text>'+mainmeta['author']+'</text>\n</docAuthor>'
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
        with open('data/kindle/default/opf_header', 'r', encoding='utf-8') as a_header:
            header = a_header.read()
        package = '<package unique-identifier="'+mainmeta['hash']+'">'
        print('DONE')
        return header+package+'\n'
    def add_metadata():
        def add_header():
            with open('data/kindle/default/opf_metadata_header', 'r', encoding='utf-8') as a_header:
                header = '<metadata>\n'+a_header.read()
            return header
        def add_common_metadata(meta):
            content = '<dc:'+meta.capitalize()+'>'+mainmeta[meta]+'</dc:'+meta.capitalize()+'>'
            return content+'\n'
        def add_author():
            content = '<dc:Creator opf:file-as="'+remove_diacritic(mainmeta['sortauthor'])+'" opf:role="aut">'+mainmeta['author']+'</dc:Creator>'
            return content+'\n'
        def add_identifier():
            content = '<dc:Identifier id="uid">'+mainmeta['hash']+'</dc:Identifier>\n'
            if mainmeta['isbn']:
                content = content+'<dc:Identifier opf:scheme="ISBN">'+mainmeta['isbn']+'</dc:Identifier>\n'
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
    copy('data/kindle/default/default.css','output')
    print('DONE')
    print('    Copying cover.jpg file... ', end='')
    copy('cover.jpg','output')
    print('DONE')

if __name__ == '__main__':
#    pass
    print('gneposis-publisher 0.1alpha by Adam Szieberth')
    print('='*80)
    
    
    data = utfize(raw())
    mainmeta = meta(data)
    mainmeta['hash'] = md5sum(options.filename)
    mainstruct = struct(data)
    mainfootnotes = footnotes(data)

    with open('output/body.html', 'w', encoding='utf-8') as a_body:
        a_body.write(kindle_html(data))

    with open('output/toc.ncx', 'w', encoding='utf-8') as a_ncx:
        a_ncx.write(kindle_ncx())
    
    with open('output/body.opf', 'w', encoding='utf-8') as a_opf:
        a_opf.write(kindle_opf())
        
    kindle_copy()