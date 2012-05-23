import re

from core.opts import path
from core.core import layout, rules, dic_t
from gntools.lines import content
from gntools.reformat import to_utf
from layout.parser import css_name, get
from layout.toctitle import location, numbers_in_titles, title
from layout.output import line_content

class NonBlockLayoutElement(ValueError): pass

def block(layoutindex):
    def header():
        if layout[layoutindex]['key'] == 'copyright':
            return '<div style="page-break-before:always"></div>\n'
        elif layout[layoutindex]['key'] == 'foreword':
            return '<a name="foreword{0}"><div class="foreword">{1}</div></a>\n'.format(layout[layoutindex]['nr'],layout[layoutindex]['title'])
        elif layout[layoutindex]['key'] == 'announcement':
            return '<div style="page-break-before:always"></div>\n'
        else:
            return ''
    def body():
        def class_string(cl):
            if cl == True or not cl:
                return ''
            else:
                return ' class="{0}"'.format(cl)
        def common_replace(s):
            return re.sub(r'_(.+?)_', r'<i>\1</i>', s)

        c = ''
        start_ind = layoutindex
        next_ind = layoutindex + 1
        next_block_ind = get(startindex=next_ind,optionkey='block', oneonly=True)
        
        while next_ind <= next_block_ind:
        
            s = layout[start_ind]['line']+1
            e = layout[next_ind]['line']
            cl = rules[layout[start_ind]['key']]['options'].get('class', None)
        
            for line in range(s,e):
                css = class_string(cl)
                l = to_utf(common_replace(line_content(line)))
                if l == '':
                    css = css[:-1] + 'empty' + css[-1]
                    l = r'&nbsp;'
                c = c + '<p{0}>{1}</p>\n'.format(css,l)
            start_ind = next_ind
            next_ind += 1
            
        return c

    if layoutindex not in get(optionkey='block'):
        raise NonBlockLayoutElement('This element does not have a block flag: {0} (in line {1})'.format(layout[layoutindex]['key'],layout[layoutindex]['line']))
        
    return header() + body()

def body(data, layout, rules):
    '''Creates the body.html data based on a given data'''
    def header(layout):
        print('\rMaking html header...'.ljust(61),end='')
        with open(path+'/data/kindle/default/html_body_header', 'r', encoding='utf-8') as a_header:
            header = a_header.read()
            p = re.compile(r'AUTHOR: TITLE')
            r = p.sub(to_utf(layout[get(key='author', oneonly=True)]['name'])+': '+to_utf(layout[get(key='title', oneonly=True)]['title']),header)
            print('[DONE]'.rjust(7))
        return r
    def frontmatter(data, layout, rules):
        def titlepage(layout, rules):
            print('\rMaking titlepage...'.ljust(61),end='')
            page = '<a name="start"/>\n<div class="{0}">{1}</div>\n<div class="{2}">{3}</div>\n'.format(css_name(get(key='author', oneonly=True),1),to_utf(layout[get(key='author', oneonly=True)]['name']),css_name(get(key='title', oneonly=True),1),to_utf(layout[get(key='title', oneonly=True)]['title']))
            if layout[get(key='title', oneonly=True)].get('subtitle',None):
                page = page + '<div class="{0}">{1}</div>\n'.format(css_name(get(key='title', oneonly=True),2), to_utf(layout[get(key='title', oneonly=True)]['subtitle']))
            print('[DONE]'.rjust(7))
            return page
        def copyrightpage(data, layout, rules):
            print('\rMaking copyrightpage...'.ljust(61),end='')
            i = get(key='copyright', oneonly=True)
            page = block(i)
            print('[DONE]'.rjust(7))
            return page
        def tableofcontents(layout,rules,depth,tocnr,toctitleind):
            print('\rMaking tocpage...'.ljust(61),end='')
            page = '<a name="toc"><div class="toc">{0}</div></a>\n'.format(dic_t['toc'])
            
            if len(get(key='intro')) == 1:
                _line = '<div class="toclvli"><a href="#intro">{0}</a></div>\n'.format(layout[get(key='intro', oneonly=True)]['title'])
                page = page + _line
            
            for i in get(optionkey='level'):
                _location = location(i,continous=numbers_in_titles['Continous'])
                if len(_location) <= depth:
                    _href = '-'.join([str(x) for x in _location])
                    _line = '<div class="toclvl{0}"><a href="#{1}">{2}</a></div>\n'.format(len(_location),_href,to_utf(title(i)))
                    page = page + _line
            print('[DONE]'.rjust(7))
            return page
        def dedication():
            return None
        def foreword():
            print('\rMaking foreword...'.ljust(61),end='')
            list_ind = get(key='foreword')
            page = ''
            for i in list_ind:
                page = page + block(i)
            print('[DONE]'.rjust(7))
            return page
        def announcement():
            print('\rMaking announcement...'.ljust(61),end='')
            list_ind = get(key='announcement')
            page = ''
            for i in list_ind:
                page = page + block(i)
            print('[DONE]'.rjust(7))
            return page
        def preface():
            return None
        return titlepage(layout, rules) + copyrightpage(data,layout, rules) + tableofcontents(layout,rules,2,(0,1),(('title',': ','subtitle'),'subtitle')) + foreword() + announcement()
    return header(layout) + frontmatter(data, layout, rules)