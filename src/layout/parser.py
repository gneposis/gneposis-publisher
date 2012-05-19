def get(layout, rules, startindex=0, endindex=None, oneonly=False, key=None, line=None, optionkey=None, optionvalue=None):
    def get_option(key, rules, optionkey, optionvalue):
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
        
        if key == layout[i]['key'] and not line:
            add = True
        elif line == layout[i]['line'] and not key:
            add = True
        elif key == layout[i]['key'] and line == layout[i]['line']:
            add = True
        elif not key and optionkey and get_option(layout[i]['key'], rules, optionkey, optionvalue) and not line:
            add = True
        elif not key and optionkey and get_option(layout[i]['key'], rules, optionkey, optionvalue) and line == layout[i]['line']:
            add = True
        else:
            add = False

        if oneonly == True and add == True:
            return i
        elif oneonly == False and add == True:
            result.append(i)
    return tuple(result)

def hasoption(rules,key,optionkey,optionvalue=None):
    if rules[key]['options'].get(optionkey,None):
        if optionvalue and rules[key]['options'][optionkey] == optionvalue:
            return True
        elif not optionvalue:
            return True
        else:
            return False
    else:
        return False
    
def optionvalues(layout, rules, optionkey='level', hierarchy=True, optionvalue=None):
    _list = []
    _set = set()
    for i in range(len(layout)):
        if hasoption(rules,layout[i]['key'],optionkey,optionvalue=optionvalue) == True:
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

def location(layout, rules, ind, continous='chapter', hierarchy=True, optionkey='level', optionvalue=None):
    def parent(layout, rules, ind, optionkey=optionkey, hierarchy=hierarchy, optionvalue=optionvalue):
        v0 = optionvalues(layout, rules, optionkey=optionkey, hierarchy=hierarchy, optionvalue=optionvalue)[ind]
        i = -1
        s = True
        while s == True and ind+i >= 0:
            v1 = optionvalues(layout, rules, optionkey=optionkey, hierarchy=hierarchy, optionvalue=optionvalue)[ind+i]
            try:
                if v1 < v0:
                    return (v0, v1, ind+i)
                else:
                    i -= 1
            except:
                i -= 1
    def count(layout, rules, ind, continous=continous, hierarchy=hierarchy, optionkey=optionkey, optionvalue=optionvalue):
        _parent = parent(layout, rules, ind, optionkey=optionkey, hierarchy=hierarchy, optionvalue=optionvalue)
        try:
            if layout[ind]['key'] in continous:
                success = True
            else:
                success = False
        except:
            success = False
                
        if success == True:
            return layout[ind]['nr']
        elif _parent:
            i = -1
            while _parent[2]+i > 0:
                v = optionvalues(layout, rules, optionkey=optionkey, hierarchy=hierarchy, optionvalue=optionvalue)[_parent[2]+i]
                if v == _parent[0]:
                    return layout[ind]['nr'] - layout[_parent[2]+i]['nr']
                else:
                    i -= 1
        return layout[ind]['nr']

    try:
        _key = layout[ind]['key']
    except:
        raise Warning('Wrong index !')


    _location = []
    loop = True
    while loop:
        _parent = parent(layout, rules, ind, optionkey=optionkey, hierarchy=hierarchy, optionvalue=optionvalue)
        _count = count(layout, rules, ind, continous=continous, hierarchy=hierarchy, optionkey=optionkey, optionvalue=optionvalue)
        
        _location.insert(0,_count)
        
        if _parent:
            ind = _parent[2]
            d = _parent[0] - _parent[1]
            while d > 1:
                _location.insert(0,None)
                d -= 1
        else:
            loop = False

    return tuple(_location)
        
def css_name(layout, rules, ind, argind):
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
