from glob import glob
from os import path
import re

import core.opts

def get_dictionary(decpath, language):
    ''' Returns the declarations dictionary for inputdata'''
    # You want this function to return the dictionary for the document language
    # only.
    return get_full_dictionary(decpath)[language]

def get_full_dictionary(decpath):
    ''' Creates the dictionary of declarations based on files in <gp.py_path>/data/languages/declarations/'''
    # You want to create a dictionary for upcoming data.
    dictionary = {}
    # Now you would like to get data from all declarations file of all
    # languages, so get their path one-by-one.
    for dict_file in glob(decpath):
        # You need to split filename and get its language key.
        path_split = path.split(dict_file)
        lang = path_split[1]
        # Now you have the key you can create a subdictionary for it.
        dictionary[lang] = {}
        # Now you want to open the declarations file, and read it.
        with open(dict_file, encoding='utf-8') as a_file:
            dictfile = a_file.read()
            # Now you want to get the declaration keys from dictfile, so you
            # will use a loop and indexing.
            s = True
            i = 0
            while s:
                # You want to search for a row which is not starting with an #,
                # but contains the declaration followed by a : with zero or
                # more whitespace(s) before and after followed by the key part
                # until the end of the line (excluding trailing whitespaces).
                p = re.compile(r'^(?!#)(?P<declaration>.+?)\s{0,}:\s{0,}(?P<key>.+?)\s{0,}$', flags=re.M)
                # You want to search for the pattern in the file from the
                # actual index to the end. If no match, 's' returns None and
                # the loop will stop.
                s = p.search(dictfile[i:])
                if s:
                    # If match then you want to add the declaration to the
                    # dictionary.
                    dictionary[lang][s.group('declaration')] = s.group('key')
                    # Now you want to increment the index with the end of the
                    # match.
                    i += s.end()
    return dictionary

def get_language(data, decpath):
    ''' Gets language key from beginning of inputdata:
    
    If inputdata begins with '{hu}' or '{HU}' it returns 'hu' if there is a
    hu file in /data/languages/declarations/.
    
    If inputdata begins with '{AUTHOR ...}' or '{TITLE ...}' it returns
    'en' since it will find AUTHOR or TITLE as a valid author or title 
    declaration in the english declaration file. Same with '{SZERZŐ ...}'
    for hungarian; this returns 'hu'.
    '''
    # You want to search for the very first declaration of inputdata.
    s = re.search(r'^{(?P<key>.+?)\s|}', data)
    # Now you want to check all languages. 'k' returns their keys.
    for k in list(get_full_dictionary(decpath).keys()):
        # If the very first declaration is the actual key, you are done.
        # This works for '{HU}' kind language declaration.  
        if s.group('key').lower() == k:
            return k
        # Else you want to check all the keys of the actual language for
        # matching. 
        else:
            for l in list(get_full_dictionary(decpath)[k].keys()):
                if s.group('key') == l:
                    # Now you only want allow 'k' to be the language if
                    # the respectable value in the fulldictionary is 'author'
                    # or 'title'.
                    if get_full_dictionary(decpath)[k][l] == 'author' or get_full_dictionary(decpath)[k][l] == 'title':
                        return k

def language():
    with open(core.opts.file, encoding='utf-8') as a_file:
        return get_language(a_file.read(),core.opts.dec_path).lower()

def make(path):
    path_map = ('declarations', 'titles')
    i = 0
    while path[-len(path_map[i])-2:-2] != path_map[i]:
        i += 1
    _dictionary = get_dictionary(path, language())
    return _dictionary