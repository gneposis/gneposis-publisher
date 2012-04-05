'''
Created on Apr 2, 2012

@author: adam szieberth
'''

import os
import glob
import re
from optparse import OptionParser

parser = OptionParser()
parser.add_option('-f', '--file', action='store', type='string', dest='filename')
(options, args) = parser.parse_args()


metas = ('author', 'title', 'subtitle')
structs = ('part', 'chapter', 'intro')
depth = {'part': 1, 'chapter': 2, 'intro': 'intro'}

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
    meta = {}
    for m in metas:
        p = re.compile(r'{'+dictionary()[language()][m]+' (?P<'+m+'>.+?)}')
        s = p.search(gp)
        meta[m] = s.group(m)
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

def kindelize(gp):
    def htmlize(gp):
        saved_footnotes = []
        def remove_meta(gp):
            print('Remove metadata... ', end='')
            r = gp
            for m in metas:
                p = re.compile(r'{'+dictionary()[language()][m]+' (.+?)}\n')
                r = re.sub(p, r'', r)
            print('DONE')
            return r
        def add_header(gp):
            print('Generating header... ', end='')
            header = open('data/kindle/default/html_body_header', encoding='utf-8')
            p = re.compile(r'AUTHOR: TITLE')
            r = p.sub(meta(utfize(raw()))['author']+': '+meta(utfize(raw()))['title'],header.read())
            header.close()
            print('DONE')
            return r + gp
        def conv_br(gp):
            print('Convert linebreaks... ', end='')
            p = re.compile(r'\s{0,}?\\\\')
            r = re.sub(p, r'<br/>', gp)
            print('DONE')
            return r
        def conv_emph(gp):
            print('Convert emphasized parts... ', end='')
            p = re.compile(r'{'+dictionary()[language()]['emph']+' (.+?)}')
            r = re.sub(p, r'<i>\1</i>', gp)
            print('DONE')
            return r
        def conv_p(gp):
            print('Convert paragraphs... ', end='')
            p1 = re.compile(r'\n\n(?!{)')
            r1 = re.sub(p1, r'\n<p>', gp)
            p2 = re.compile(r'^<p>(.+?)$', re.M)
            r2 = re.sub(p2, r'<p>\1</p>', r1)
            print('DONE')
            return r2
        def conv_paragraph(gp):
            print('Convert paragraph titles... ', end='')
            p = re.compile(r'{'+dictionary()[language()]['paragraph']+' (.+?)}')
            r = re.sub(p, r'<p class="paragraph">\1</p>', gp)
            print('DONE')
            return r
        def conv_right(gp):
            print('Convert right indented blocks... ', end='')
            p = re.compile(r'{'+dictionary()[language()]['right']+' (.+?)}')
            r = re.sub(p, r'<div align="right">\1</div>', gp)
            print('DONE')
            return r
        def conv_footnotes(gp):
            nonlocal saved_footnotes
            saved_footnotes = footnotes(gp)
            print('Convert inline footnotes... ', end='')
            r = gp
            for f in range(len(footnotes(gp))):
                p = re.compile('{'+dictionary()[language()]['footnote']+' '+get_re_string(footnotes(gp)[f][3])+'}')
                r = p.sub('<a name="fn_name_'+str(footnotes(gp)[f][2])+'" href="#fn_index_'+str(footnotes(gp)[f][2])+'"><span class="footnote"><sup>'+str(footnotes(gp)[f][2])+'</sup></span></a>',r)
            print('DONE')
            return r
        def add_footnotes(gp):
            print('Generating footnotes... ', end='')
            gp = gp + '\n\n<a name="footnotes"><div class="footnotes">'+dictionary()[language()]['notes']+':</div></a>\n'
            for f in range(len(saved_footnotes)):
                footnote = '<div class="footnoteitem"><a name="fn_index_'+str(saved_footnotes[f][2])+'" href="#fn_name_'+str(saved_footnotes[f][2])+'">['+str(saved_footnotes[f][2])+']</a>'+saved_footnotes[f][3]+'</div>\n'
                gp = gp + footnote
            print('DONE')
            return gp
        def add_footer(gp):
            print('Generating footer... ', end='')
            gp = gp + '\n</body>\n</html>'
            print('DONE')
            return gp
        def conv_struct(gp):
            print('Convert text parts... ', end='')
            r = gp
            for s in range(len(struct(gp))):
                if struct(gp)[s][5] is None:
                    p = re.compile('{'+dictionary()[language()][struct(gp)[s][3]]+' '+get_re_string(struct(gp)[s][4])+'}')
                    r = p.sub('<a name="'+str(struct(gp)[s][2][0])+'-'+str(struct(gp)[s][2][1])+'"><div class="'+struct(gp)[s][3]+'_alone">'+struct(gp)[s][4]+'</div></a>',r)
                else:
                    p = re.compile('{'+dictionary()[language()][struct(gp)[s][3]]+' '+get_re_string(struct(gp)[s][4])+' :: '+get_re_string(struct(gp)[s][5])+'}')
                    r = p.sub('<a name="'+str(struct(gp)[s][2][0])+'-'+str(struct(gp)[s][2][1])+'"><div class="'+struct(gp)[s][3]+'_withtitle">'+struct(gp)[s][4]+'</div></a>\n<div class="'+struct(gp)[s][3]+'title">'+struct(gp)[s][5]+'</div>',r)
            print('DONE')
            return r
        def conv_verse(gp):
            print('Convert verse... ', end='')
            p = re.compile(r'{'+dictionary()[language()]['verse']+' (.+?)}', re.S)
            r = re.sub(p, r'<div class="verse">\1</div>', gp)
            print('DONE')
            return r
        gp = remove_meta(gp)
        gp = add_header(gp)
        gp = conv_emph(gp)
        gp = conv_right(gp)
        gp = conv_p(gp)
        gp = conv_paragraph(gp)
        gp = conv_footnotes(gp)
        gp = add_footnotes(gp)
        gp = conv_struct(gp)
        gp = conv_verse(gp)
        gp = conv_br(gp)
        gp = add_footer(gp)
        return gp
    return htmlize(gp)

if __name__ == '__main__':
#    pass
    with open('output/body.html', 'w', encoding='utf-8') as a_body:
        a_body.write(kindelize(utfize(raw())))
