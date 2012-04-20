import re

def restg(inputstring):
    string = inputstring
    string = string.replace('\\','\\\\')
    string = string.replace('.','\.')
    string = string.replace('^','\^')
    string = string.replace('$','\$')
    string = string.replace('*','\*')
    string = string.replace('+','\+')
    string = string.replace('?','\?')
    string = string.replace('{','\{')
    string = string.replace('}','\}')
    string = string.replace('[','\[')
    string = string.replace(']','\]')
    string = string.replace('|','\|')
    string = string.replace('(','\(')
    string = string.replace(')','\)')
    return string

def locnewlines(inputdata):
    '''Returns the locations of newlines of a given data'''
    newlines = {}
    i = 1
    for m in re.finditer(r'^', inputdata, flags=re.M):
        newlines[i] = m.span()[0]
        i += 1
#        print(m.span()[0])
    return newlines

def linenr(loc, inputdata):
    '''Returns the line number of a location in a given data'''
    _lines = locnewlines(inputdata)
    if _lines[len(_lines)] <= loc and len(inputdata) > loc:
        return len(_lines)
    else:
        for l in range(2,len(_lines)):
            if _lines[l-1] <= loc and _lines[l] > loc:
                return l-1
            
def line(linenr, inputdata):
    '''Returns the content of a given line in a given data''' 
    _lines = locnewlines(inputdata)  
    return inputdata[_lines[linenr]:_lines.get(linenr+1, len(inputdata)+1)-1]