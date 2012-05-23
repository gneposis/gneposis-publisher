import re

from core.opts import path
from core.core import dic_t
from gntools.lines import content
from gntools.reformat import to_utf
from layout.parser import css_name, get
from layout.toctitle import location, numbers_in_titles, title

def body(data, layout, rules):
    '''Creates the body.html data based on a given data'''
    def header(layout):
        print('\rMaking html header...'.ljust(61),end='')
        with open(path+'/data/kindle/default/html_body_header', 'r', encoding='utf-8') as a_header:
            header = a_header.read()
            p = re.compile(r'AUTHOR: TITLE')
            r = p.sub(to_utf(layout[get(layout,rules,key='author', oneonly=True)]['name'])+': '+to_utf(layout[get(layout,rules,key='title', oneonly=True)]['title']),header)
            print('[DONE]'.rjust(7))
        return r
    def frontmatter(data, layout, rules):
        def titlepage(layout, rules):
            print('\rMaking titlepage...'.ljust(61),end='')
            page = '<a name="start"/>\n<div class="{0}">{1}</div>\n<div class="{2}">{3}</div>\n'.format(css_name(layout,rules,get(layout,rules,key='author', oneonly=True),1),to_utf(layout[get(layout,rules,key='author', oneonly=True)]['name']),css_name(layout,rules,get(layout,rules,key='title', oneonly=True),1),to_utf(layout[get(layout,rules,key='title', oneonly=True)]['title']))
            if layout[get(layout,rules,key='title', oneonly=True)].get('subtitle',None):
                page = page + '<div class="{0}">{1}</div>\n'.format(css_name(layout,rules,get(layout,rules,key='title', oneonly=True),2), to_utf(layout[get(layout,rules,key='title', oneonly=True)]['subtitle']))
            print('[DONE]'.rjust(7))
            return page
        def copyrightpage(data, layout, rules):
            print('\rMaking copyrightpage...'.ljust(61),end='')
            i = get(layout,rules,key='copyright', oneonly=True)
            _start = layout[i]['line']+1
            _end = layout[i+1]['line']
            page = '<div style="page-break-before:always"></div>\n'
            for line in range(_start,_end):
                _css = css_name(layout,rules,i,None)
                _line = to_utf(content(line,data))
                if _line == '':
                    _css = _css + 'empty'
                    _line = r'&nbsp;'
                page = page + '<div class="{0}">{1}</div>\n'.format(_css,_line)
            print('[DONE]'.rjust(7))
            return page
        def tableofcontents(layout,rules,depth,tocnr,toctitleind):
            print('\rMaking tocpage...'.ljust(61),end='')
            page = '<a name="toc"><div class="toc">{0}</div></a>\n'.format(dic_t['toc'])
            
            if len(get(layout,rules,key='intro')) == 1:
                _line = '<div class="toclvli"><a href="#intro">{0}</a></div>\n'.format(layout[get(layout,rules,key='intro')[0]]['title'])
                page = page + _line
            
            for i in get(layout,rules,optionkey='level'):
                _location = location(layout,rules,i,continous=numbers_in_titles['Continous'])
                if len(_location) <= depth:
                    _href = '-'.join([str(x) for x in _location])
                    _line = '<div class="toclvl{0}"><a href="#{1}">{2}</a></div>\n'.format(len(_location),_href,to_utf(title(i)))
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