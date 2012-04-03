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

gp_dictionary = {}
def get_gp_dictionary():
    global gp_dictionary
    for dict_file in glob.glob('data/languages/*'):
        path_split = os.path.split(dict_file)
        lang = path_split[1]
        gp_dictionary[lang] = {}
        line_number = 0
        with open(dict_file, encoding='utf-8') as a_file:
            for a_line in a_file:
                line_number += 1
                key = re.split('\W+?', a_line)[0]
                value = re.split('\W+?', a_line)[2]
                gp_dictionary[lang][key] = value

def get_language():
    with open(options.filename, encoding='utf-8') as a_file:
        a_file.seek(0)
        first_line = a_file.readline()
        key = re.split('\W+?', first_line)[1]
        for language in gp_dictionary:
            if gp_dictionary[language]['author'] == key or gp_dictionary[language]['title'] == key:
                return language

rawdata = None
def parse_input_file():
    global rawdata
    with open(options.filename, encoding='utf-8') as a_file:
        rawdata = a_file.read()
        # deal with preamble
        rawdata = re.sub(r'}\n{', r'}\\\\\n{', rawdata)

        # \n\n to @@@ and \n to \s and back with @@@s
        rawdata = re.sub(r'\n\n', r'@@@', rawdata)
        rawdata = re.sub(r'\n', r' ', rawdata)
        rawdata = re.sub(r'@@@', r'\n\n', rawdata)
        
        # deal with linebreaks
        rawdata = re.sub(r'\\\\\s{0,}', r'\\\\\n', rawdata)
        
        # deal with preamble again
        rawdata = re.sub(r'}\\\\\n{', r'}\n{', rawdata)

def utfize(gp_input):
    output = gp_input
    output = re.sub('--', '–', output)
    output = re.sub(',,', '„', output)
    output = re.sub("''", "”", output)
    return output

def get_meta():
    def get_author():
        p = re.compile(r'{'+gp_dictionary[language]['author']+' (?P<author>.+?)}')
        m = p.search(source_data)
        return m.group('author')
    def get_subtitle():
        p = re.compile(r'{'+gp_dictionary[language]['subtitle']+' (?P<subtitle>.+?)}')
        m = p.search(source_data)
        return m.group('subtitle')
    def get_title():
        p = re.compile(r'{'+gp_dictionary[language]['title']+' (?P<title>.+?)}')
        m = p.search(source_data)
        return m.group('title')
    return {'author': get_author(),
            'subtitle': get_subtitle(),
            'title': get_title()}

def get_parts():
    parts = []
    searching = True
    partindex = 1
    offset = 0
    while searching:
        p = re.compile('{'+gp_dictionary[language]['part']+' (?P<part>.+?)}')
        m = p.search(source_data[offset:])
        if m:
            p2 = re.compile(r'(?P<parttitle>.+?)\s::\s(?P<partsubtitle>.+?)$')
            m1 = p2.search(m.group('part'))
            parts.append((offset+m.start(), offset+m.end(),'PART', m1.group('parttitle'), m1.group('partsubtitle')))
            partindex += 1
            offset += m.end()
        else: 
            searching = False
    return parts

def get_chapters():
    chapters = []
    searching = True
    chapterindex = 1
    offset = 0
    while searching:
        p = re.compile('{'+gp_dictionary[language]['chapter']+' (?P<chapter>.+?)}')
        m = p.search(source_data[offset:])
        if m:
            p2 = re.compile(r'(?P<chaptertitle>.+?)\s::\s(?P<chaptersubtitle>.+?)$')
            m1 = p2.search(m.group('chapter'))
            chapters.append((offset+m.start(), offset+m.end(),'CHAPTER', m1.group('chaptertitle'), m1.group('chaptersubtitle')))
            chapterindex += 1
            offset += m.end()
        else: 
            searching = False
    return chapters

def get_struct_anchors():
    struct_anchors = []
    parts = get_parts()
    i = 0
    while i < len(parts):
        struct_anchors.append(parts[i][0])
        i +=1
    chapters = get_chapters()
    i = 0
    while i < len(chapters):
        struct_anchors.append(chapters[i][0])
        i +=1
    struct_anchors.sort()
    return struct_anchors

def get_struct():
    struct = []
    tempstruct = get_parts()
    tempstruct.extend(get_chapters())
    for i in range(len(get_struct_anchors())):
        for j in range(len(tempstruct)):
            if get_struct_anchors()[i] == tempstruct[j][0]:
                struct.append(tempstruct[j])
    return struct
    

def htmlize():
    with open('output/body.html', 'a', encoding='utf-8') as a_body:
        with open('data/kindle/default/html_body_header', encoding='utf-8') as a_header:
            p = re.compile(r'AUTHOR: TITLE')
            new_header = p.sub(meta['author']+': '+meta['title'],a_header.read())
        a_body.write(new_header)

#def htmlize(gp_input):
#    def conv_emph(htmlize_input):
#        pattern = re.compile(r'{'+gp_dictionary[language]['emph']+' (.+?)}')
#        output = re.sub(pattern, r'<i>\1</i>', htmlize_input)
#        return output
#    output = conv_emph(gp_input)
#    return output
        

if __name__ == '__main__':
#    pass
    get_gp_dictionary()
    language = get_language()
    parse_input_file()
    source_data = utfize(rawdata)
    meta = get_meta()
    struct = get_struct()

