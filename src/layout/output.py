from .create import layout
from .parser import get
from gntools.lines import content

def line(data, rules, dictionary, linenr):
    _layout = layout(data,rules,dictionary)
    _declarations = get(_layout, rules, line=linenr, startindex=0, endindex=None, oneonly=False)
    _line = content(linenr,data)
    remaining = len(_declarations)
    done = 0
    generating = True
    
    content = []
    
    while generating:
        # whole phase
        if remaining == 0 and done == 0:
            s = None
            e = None
            add = False
        # opening phase
        elif remaining > 0 and done == 0:
            s = None
            e = _layout[_declarations[done]]['column'][0]
            add = True
        # inter phase
        elif remaining > 0 and done > 0:
            s = _layout[_declarations[done-1]]['column'][1]
            e = _layout[_declarations[done]]['column'][0]
            add = True
        # end phase
        elif remaining == 0 and done > 0:
            s = _layout[_declarations[done-1]]['column'][1]
            e = None
            add = False
            generating = False
        
        content.append(_line[s:e])
        
        if add:
            content.append(_declarations[done])
            remaining -= 1
            done += 1

    return tuple(content)