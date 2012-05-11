import re

import gp
import gntools
from gpconverter import utf
import opts

def body(data, layout, rules):
    '''Creates the body.html data based on a given data'''
    def header(layout):
        print('\rMaking html header...'.ljust(61),end='')
        with open(opts.path+'/data/kindle/default/html_body_header', 'r', encoding='utf-8') as a_header:
            header = a_header.read()
            p = re.compile(r'AUTHOR: TITLE')
            r = p.sub(utf(layout[gp.layout.get(layout,rules,key='author', oneonly=True)]['name'])+': '+utf(layout[gp.layout.get(layout,rules,key='title', oneonly=True)]['title']),header)
            print('[DONE]'.rjust(7))
        return r
    def frontmatter(data, layout, rules):
        def titlepage(layout, rules):
            print('\rMaking titlepage...'.ljust(61),end='')
            page = '<a name="start"/>\n<div class="{0}">{1}</div>\n<div class="{2}">{3}</div>\n'.format(gp.layout.css(layout,rules,gp.layout.get(layout,rules,key='author', oneonly=True),1),utf(layout[gp.layout.get(layout,rules,key='author', oneonly=True)]['name']),gp.layout.css(layout,rules,gp.layout.get(layout,rules,key='title', oneonly=True),1),utf(layout[gp.layout.get(layout,rules,key='title', oneonly=True)]['title']))
            if layout[gp.layout.get(layout,rules,key='title', oneonly=True)].get('subtitle',None):
                page = page + '<div class="{0}">{1}</div>\n'.format(gp.layout.css(layout,rules,gp.layout.get(layout,rules,key='title', oneonly=True),2), utf(layout[gp.layout.get(layout,rules,key='title', oneonly=True)]['subtitle']))
            print('[DONE]'.rjust(7))
            return page
        def copyrightpage(data, layout, rules):
            print('\rMaking copyrightpage...'.ljust(61),end='')
            i = gp.layout.get(layout,rules,key='copyright', oneonly=True)
            _start = layout[i]['line']+1
            _end = layout[i+1]['line']
            page = '<div style="page-break-before:always"></div>\n'
            for line in range(_start,_end):
                _css = gp.layout.css(layout,rules,i,None)
                _line = utf(gntools.line(line,data))
                if _line == '':
                    _css = _css + 'empty'
                    _line = r'&nbsp;'
                page = page + '<div class="{0}">{1}</div>\n'.format(_css,_line)
            print('[DONE]'.rjust(7))
            return page
        def tableofcontents(layout,rules,depth,tocnr,toctitleind):
            print('\rMaking tocpage...'.ljust(61),end='')
            def toctitletext(layoutelement, location, tocnr, toctitleind):
                _depth = len(location)
                _location = list(location)
                for i in range(_depth):
                    try:
                        if tocnr[i] == False or tocnr[i] == 0:
                            _location[i] = None
                    except:
                        None
                
                while _location.count(None)>0:
                    _location.remove(None)
                
                _location = '.'.join([str(x) for x in _location])
                
                if _location != '':
                    _location = _location + '. '
                
                try:
                    titlerule = toctitleind[_depth-1]
                except:
                    titlerule = 'title'
                
                if titlerule == str(titlerule):
                    _title = layoutelement[titlerule]
                else:
                    _title = ''
                    for i in range(len(titlerule)):
                        try:
                            _title = _title + layoutelement[titlerule[i]]
                        except:
                            _title = _title + titlerule[i]
                    
                return '{0}{1}'.format(_location,_title)
            page = '<a name="toc"><div class="toc">{0}</div></a>\n'.format('Table of Contents')
            for i in gp.layout.get(layout,rules,optionkey='level'):
                _location = gp.layout.location(layout,rules,i)
                if len(_location) <= depth:
                    _href = '-'.join([str(x) for x in _location])
                    _line = '<div class="toclvl{0}"><a href="#{1}">{2}</a></div>\n'.format(len(_location),_href,utf(toctitletext(layout[i], _location, tocnr, toctitleind)))
                    page = page + _line
            print('[DONE]'.rjust(7))
            return page
        def dedication():
            return None
        def foreword():
            return None
        def preface():
            return None
        return titlepage(layout, rules) + copyrightpage(data,layout, rules) + tableofcontents(layout,rules,2,(0,1),(('title',': ','subtitle'),'subtitle'))
    return header(layout) + frontmatter(data, layout, rules)