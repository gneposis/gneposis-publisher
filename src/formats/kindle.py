import re

from core.opts import path
from core.core import layout, rules, dic_t
from gntools.lines import content
from gntools.reformat import to_utf
from layout.parser import css_name, get
from layout.toctitle import location, numbers_in_titles, title
from layout.output import line_content

class NonBlockLayoutElement(ValueError): pass


# key, header, body, footer
block_map = (('announcement', '"<div style="page-break-before:always"></div>\\n"', '"<p{0}>{1}</p>\\n".format(css, l)', '""'),
             ('copyright', '"<div style="page-break-before:always"></div>\\n"', '"<div{0}>{1}</div>\\n".format(css, l)', '""'),
             ('foreword', '"<a name="foreword{0}"><div class="foreword">{1}</div></a>\\n".format(layout[layoutindex]["nr"],layout[layoutindex]["title"])', '"<p{0}>{1}</p>\\n".format(css, l)', '""'),
             )


def block(layoutindex):
    def header():
        for i in block_map:
            if layout[layoutindex]['key'] == i[0]:
                return eval(i[1])
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
        
        while isinstance(next_block_ind, int) == True and next_ind <= next_block_ind:
        
            s = layout[start_ind]['line']+1
            e = layout[next_ind]['line']
            cl = rules[layout[start_ind]['key']]['options'].get('class', None)
        
            for line in range(s,e):
                print(line)
                css = class_string(cl)
                l = to_utf(common_replace(line_content(line)))
                if l == '':
                    css = css[:-1] + 'empty' + css[-1]
                    l = r'&nbsp;'
                for i in block_map:
                    if layout[layoutindex]['key'] == i[0]:
                        c1 = eval(i[2]) 
                    else:
                        c1 = ''
                c = c + c1
            start_ind = next_ind
            next_ind += 1
        return c
    def footer():
        for i in block_map:
            if layout[layoutindex]['key'] == i[0]:
                return eval(i[3])
            else:
                return ''

    if layoutindex not in get(optionkey='block') and layout[layoutindex]['key'] != 'copyright':
        raise NonBlockLayoutElement('This element does not have a block flag: {0} (in line {1})'.format(layout[layoutindex]['key'],layout[layoutindex]['line']))
        
    return header() + body() + footer()

def make_body_html():
    '''Creates the body.html data based on a given data'''
    def header():
        print('\rMaking html header...'.ljust(61),end='')
        with open(path+'/data/kindle/default/html_body_header', 'r', encoding='utf-8') as a_header:
            header = a_header.read()
            p = re.compile(r'AUTHOR: TITLE')
            r = p.sub(to_utf(layout[get(key='author', oneonly=True)]['name'])+': '+to_utf(layout[get(key='title', oneonly=True)]['title']),header)
            print('[DONE]'.rjust(7))
        return r
    def body():
        def titlepage():
            print('\rMaking titlepage...'.ljust(61),end='')
            page = '<a name="start"/>\n<div class="{0}">{1}</div>\n<div class="{2}">{3}</div>\n'.format(css_name(get(key='author', oneonly=True),1),to_utf(layout[get(key='author', oneonly=True)]['name']),css_name(get(key='title', oneonly=True),1),to_utf(layout[get(key='title', oneonly=True)]['title']))
            if layout[get(key='title', oneonly=True)].get('subtitle',None):
                page = page + '<div class="{0}">{1}</div>\n'.format(css_name(get(key='title', oneonly=True),2), to_utf(layout[get(key='title', oneonly=True)]['subtitle']))
            print('[DONE]'.rjust(7))
            return page
        def copyrightpage():
            print('\rMaking copyrightpage...'.ljust(61),end='')
            i = get(key='copyright', oneonly=True)
            page = block(i)
            print('[DONE]'.rjust(7))
            return page
        def tableofcontents(depth):
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
        def anything_else():
            print('\rMaking rest of body...'.ljust(61),end='')
            list_ind = get(optionkey='block')
            page = ''
            for i in list_ind:
                page = page + block(i)
            print('[DONE]'.rjust(7))
            return page
        return titlepage() + copyrightpage() + tableofcontents(2) + anything_else()
    return header() + body()