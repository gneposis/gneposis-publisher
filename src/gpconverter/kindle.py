import re

import gp
import gnparser
from gpconverter import utf
import opts

def body(data, struct):
    '''Creates the body.html data based on a given data'''
    def header(struct):
        with open(opts.path+'/data/kindle/default/html_body_header', 'r', encoding='utf-8') as a_header:
            header = a_header.read()
            p = re.compile(r'AUTHOR: TITLE')
            r = p.sub(utf(gp.dec_ind(struct, 'author', 'name'))+': '+utf(gp.dec_ind(struct, 'title', 'title')),header)
        return r
    def frontmatter(struct):
        def titlepage(struct):
            page = '<a name="start"/>\n<div class="author">'+utf(gp.dec_ind(struct, 'author', 'name'))+'</div>\n'+'<div class="title">'+utf(gp.dec_ind(struct, 'title', 'title'))+'</div>\n'
            if gp.dec_ind(struct, 'title', 'subtitle'):
                page = page + '<div class="subtitle">'+utf(gp.dec_ind(struct, 'title', 'subtitle'))+'</div>\n'
            return page
        def copyrightpage(data,struct):
            _start = gp.dec_ind(struct, 'copyright', 'line')+1
            _end = struct[gp.dec_ind(struct, 'copyright', 'nextany')]['line']
            page = '<div style="page-break-before:always"></div>\n'
            for line in range(_start,_end):
                page = page + '<div class="copyrightpagetext">' + utf(gnparser.line(line,data)) + '</div>\n'
            return page
        def tableofcontents():
            return None
        def dedication():
            return None
        def foreword():
            return None
        def preface():
            return None
        return titlepage(struct) + copyrightpage(data,struct)
    return header(struct) + frontmatter(struct)