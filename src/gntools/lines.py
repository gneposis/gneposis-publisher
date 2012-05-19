import re

def newlines(inputdata):
    '''Returns the locations of newlines of a given data'''
    newlines = []
    for m in re.finditer(r'^', inputdata, flags=re.M):
        newlines.append(m.span()[0])
    return tuple(newlines)

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
            
def content(linenr, inputdata):
    '''Returns the content of a given line in a given data'''
    return inputdata[newlines(inputdata)[linenr-1]:newlines(inputdata)[linenr]-1]
