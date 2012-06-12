def newlines(inputdata):
    '''Returns the locations of newlines of a given data'''
    newlines = [0]
    i = 0
    while i >= 0:
        i = inputdata.find('\n', i+1)
        if i >= 0:
            newlines.append(i+1)
    return tuple(newlines)

def lines(inputdata, lineindex=None):
    '''returns the contents of lines or a particular line'''
    l = []
    _newlines = newlines(inputdata)
    for i in range(len(_newlines)):
        if i == len(_newlines) - 1:
            e = None
        else:
            e = _newlines[i+1]
        l.append(inputdata[_newlines[i]:e])
    if lineindex:
        return l[lineindex]
    else:
        return tuple(l)

def nr(loc, inputdata):
    '''Returns the line number of a location in a given data'''
    _newlines = newlines(inputdata)
    for i in _newlines:
        ind = _newlines.index(i)
        if i == _newlines[-1]:
            e = len(inputdata)
        else:
            e = _newlines[ind+1]

        if i <= loc < e:
            return ind + 1
