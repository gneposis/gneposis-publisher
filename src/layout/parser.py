from core.core import layout, rules

def get(startindex=0, endindex=None, oneonly=False, key=None, line=None, optionkey=None, optionvalue=None):
    def get_option(key):
        if optionkey and optionvalue:
            if optionvalue == rules[key]['options'].get(optionkey, False):
                return True
        elif optionkey and not optionvalue:
            if rules[key]['options'].get(optionkey, None):
                return True
        else:
            return None
           
    if not endindex:
        endindex = len(layout)
    
    result = []
    
    for i in range(startindex,endindex):
        
        if not line and key == layout[i]['key']:
            add = True
        elif not line and not key and optionkey and get_option(layout[i]['key']):
            add = True
        elif line == layout[i]['line'] and not key and not optionkey:
            add = True
        elif line == layout[i]['line'] and key == layout[i]['key']:
            add = True
        elif line == layout[i]['line'] and not key and optionkey and get_option(layout[i]['key']):
            add = True
        else:
            add = False

        if oneonly == True and add == True:
            return i
        elif oneonly == False and add == True:
            result.append(i)
    return tuple(result)

def hasoption(key,optionkey='level',optionvalue=None):
    if rules[key]['options'].get(optionkey,None):
        if optionvalue and rules[key]['options'][optionkey] == optionvalue:
            return True
        elif not optionvalue:
            return True
        else:
            return False
    else:
        return False

def optionvalues(optionkey='level', hierarchy=True, optionvalue=None):
    _list = []
    _set = set()
    for i in range(len(layout)):
        if hasoption(layout[i]['key'],optionkey,optionvalue=optionvalue) == True:
            value = rules[layout[i]['key']]['options'][optionkey]
            _list.append(value)
            _set.add(value)
        else:
            _list.append(None)
    if hierarchy:
        _hierarchy = sorted(_set)
        for i in range(len(_list)):
            if _list[i]:
                _list[i] = _hierarchy.index(_list[i])
    return _list

def css_name(ind, argind):
    css = ''
    if layout[ind].get('css',None):
        css = layout[ind]['css']
    else:
        css = layout[ind]['key']
    if argind and argind != 0:
        try:
            arg = rules[layout[ind]['key']][min(argind,rules[layout[ind]['key']]['reqargs']+rules[layout[ind]['key']]['optargs'])]
        except:
            arg = ''
        if arg != css:
            css = css + arg
    return css