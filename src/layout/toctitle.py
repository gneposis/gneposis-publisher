import re

from .parser import get, optionvalues
from gntools import numtext
from gntools.numtext import *
from gntools.roman import to_roman
from core.core import layout, rules, language

class NonConsistentNumberingError(ValueError): pass
class MoreThanOneContinouslyNumberedDivisionsError(ValueError): pass

NUMBER_HIER = ('text','roman','arabic')

NUMBER_EVALS = { 'text'   : 'getattr(numtext,language).to_text_ord(n)',
                 'roman'  : 'to_roman(n)',
                 'arabic' : 'str(n)' }


def _hierarchy():
    values = optionvalues()
    level = 0
    loop = True
    result = []
    while loop:
        try:
            result.append(layout[values.index(level)]['key'])
            level +=1
        except:
            loop = False
    return tuple(result)

hierarchy = _hierarchy()

def location(ind, continous=None):
    def parent(ind):
        v0 = optionvalues()[ind]
        i = -1
        s = True
        while s == True and ind+i >= 0:
            v1 = optionvalues()[ind+i]
            try:
                if v1 < v0:
                    return (v0, v1, ind+i)
                else:
                    i -= 1
            except:
                i -= 1
    def count(ind):
        _parent = parent(ind)
        try:
            if layout[ind]['key'] == continous:
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
                v = optionvalues()[_parent[2]+i]
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
        _parent = parent(ind)
        _count = count(ind)
        
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

def _numbers_in_titles():
    def check(n_type):
        n = location(ind, continous=None)[-1]
        if re.search(r'\b'+eval(NUMBER_EVALS[n_type])+r'\b',content):
            return n_type
        else:
            n = location(ind, continous=division)[-1]
            if re.search(r'\b'+eval(NUMBER_EVALS[n_type])+r'\b',content):
                result['Continous'].add(division)
                return n_type
            else:
                return None
    result = dict()
    result['Continous'] = set()
    for division in hierarchy:
        result[division] = ''
        ind_list = get(key=division)
        for ind in ind_list:
            content = layout[ind]['title'].lower()
            if result[division] == '':
                for n_type in NUMBER_HIER:
                    if result[division] == '':
                        result[division] = check(n_type)
            elif result[division] and result[division] != check(result[division]):
                raise NonConsistentNumberingError('Wrong title numbering: "{0}" followed by "{1}".'.format(layout[ind_list[ind_list.index(ind)-1]]['title'],layout[ind]['title']))
    if len(result['Continous']) == 0:
        result['Continous'] = None
    elif len(result['Continous']) > 1:
        raise MoreThanOneContinouslyNumberedDivisionsError('Two or more divisions were numbered continously')
    else:
        result['Continous'] = result['Continous'].pop()
    return result

numbers_in_titles = _numbers_in_titles()

def title(layoutindex):
    def get_numbering():
        if hierarchy.index(_key) < hierarchy.index(cap):
            return ''
        elif hierarchy.index(_key) == hierarchy.index(cap):
            if layout[layoutindex].get('subtitle', None):
                return str(location(layoutindex, continous=_key)[-1]) + '. '
            else:
                return ''
        else:
            return str(location(layoutindex, continous=None)[-1]) + '. '
                
    def get_title():
        if hierarchy.index(_key) < hierarchy.index(cap):
            if layout[layoutindex].get('subtitle', None):
                return layout[layoutindex]['title'] + ': ' + layout[layoutindex]['subtitle']
            else:
                return layout[layoutindex]['title']
        else:
            if numbers_in_titles[_key]:
                if layout[layoutindex].get('subtitle', None):
                    return layout[layoutindex]['subtitle']
                else:
                    return layout[layoutindex]['title']
            else:
                return layout[layoutindex]['title']
                
    
    if numbers_in_titles['Continous']:
        cap = numbers_in_titles['Continous']
    else:
        cap = 0
    
    _key = layout[layoutindex]['key']
    
    return get_numbering() + get_title()
