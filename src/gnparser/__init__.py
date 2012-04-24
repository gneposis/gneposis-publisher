import re
import unicodedata
import hashlib
from functools import partial

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

def remove_diacritic(i):
    # This code is from http://code.activestate.com/recipes/576648-remove-diatrical-marks-including-accents-from-stri/
    ''' Accept a unicode string, and return a normal string (bytes in Python 3)
    without any diacritical marks. '''
    return unicodedata.normalize('NFKD', i).encode('ASCII', 'ignore').decode()

def gethash(inputdata):
    '''Returns the md5 hash of a given data'''

def md5sum(filename):
    # Code is from http://stackoverflow.com/a/7829658
    '''Returns the md5sum of a given file'''
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
    return d.hexdigest()

def md5(data):
    # Code is from http://stackoverflow.com/a/7829658
    '''Returns the md5sum of a given file'''
    d = hashlib.md5()
    d.update(data.encode('utf-8'))
    return d.hexdigest()