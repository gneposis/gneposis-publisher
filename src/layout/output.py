from core.core import raw, layout
from .parser import get
from gntools.lines import content

def line_content(linenr):
    inline_dec = get(line=linenr, optionkey='inline')
    line_content = content(linenr, raw)
    remaining = len(inline_dec)
    
    if remaining == 0 and len(get(line=linenr)) == 0:
        return line_content
    elif remaining == 0:
        return None
     
    done = 0
    generating = True
    c = []
    while generating:
        # opening phase
        if remaining > 0 and done == 0:
            s = None
            e = layout[inline_dec[done]]['column'][0]
            add = True
        # inter phase
        elif remaining > 0 and done > 0:
            s = layout[inline_dec[done-1]]['column'][1]
            e = layout[inline_dec[done]]['column'][0]
            add = True
        # end phase
        elif remaining == 0 and done > 0:
            s = layout[inline_dec[done-1]]['column'][1]
            e = None
            add = False
            generating = False
        
        c.append(line_content[s:e])
        
        if add:
            c.append(inline_dec[done])
            remaining -= 1
            done += 1

    return tuple(c)