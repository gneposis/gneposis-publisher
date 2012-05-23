from .opts import decmainpath, decpath, file, fileext, filefile, filepath, titpath
from layout.main import get_dictionary, get_language, get_layout, get_rules, get_raw

def _f():
    with open(file, encoding='utf-8') as a_file:
        return a_file.read()

f = _f()

def _rules(pr=True):
    if pr:
        print('\rMaking rules...'.ljust(61),end='')
    with open(decmainpath, encoding='utf-8') as a_file:
        _rules = get_rules(a_file.read())
    if pr:
        print('[DONE]'.rjust(7))
    return _rules

rules = _rules()

def _language():
    return get_language(f,decpath).lower()

language = _language()

def _dictionary(pr=True):
    if pr:
        print('\rGenerating dictionaries for language: {0}'.format(language.upper()).ljust(61),end='')
    _dictionary_declarations = get_dictionary(decpath, language)
    _dictionary_titles = get_dictionary(titpath, language)
    if pr:
        print('[DONE]'.rjust(7))
    return (_dictionary_declarations, _dictionary_titles)

dictionaries = _dictionary()
dic_d = dictionaries[0]
dic_t = dictionaries[1]

def _raw(pr=True,save=False):
    raw = get_raw(f, rules, dic_d, pr=pr)
    if save:
        with open(filepath+'/'+filefile+'.raw.'+fileext, 'w', encoding='utf-8') as a_raw:
            a_raw.write(raw)
    if pr:
        print('[DONE]'.rjust(7))
    return raw

raw = _raw()

def _layout(pr=True):
    return get_layout(raw, rules, dic_d,pr=pr)

layout = _layout()