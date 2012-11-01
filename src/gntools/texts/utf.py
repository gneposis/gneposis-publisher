import re

def re_string(s):
    '''Converts a string to be able to used in re patterns.'''
    s = s.replace('\\','\\\\')
    s = s.replace('.','\.')
    s = s.replace('^','\^')
    s = s.replace('$','\$')
    s = s.replace('*','\*')
    s = s.replace('+','\+')
    s = s.replace('?','\?')
    s = s.replace('{','\{')
    s = s.replace('}','\}')
    s = s.replace('[','\[')
    s = s.replace(']','\]')
    s = s.replace('|','\|')
    s = s.replace('(','\(')
    s = s.replace(')','\)')
    return s

def remove_diacritic(s):
    ''' Accept a unicode string, and return a normal string (bytes in Python 3)
    without any diacritical marks.'''
    # This code is from http://code.activestate.com/recipes/576648-remove-diatrical-marks-including-accents-from-stri/
    return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode()

def to_utf(s):
    '''Replaces parts (characters) of string with their utf representative.'''
    def conv_fullquote(s):
        '''Convert simple quotes to leading and trailing ones.'''
        p = re.compile(r'"(.+?)"')
        r = re.sub(p, r'“\1”', s)
        return r
    # You want to replace dashes:
    s = s.replace('---','—') # Em dash
    s = s.replace('--','–') # Then en dash
    # You define a function to convert full quotes such {Q Lorem ipsum} to “Lorem
    # ipsum”. You call the function immediately.
    s = conv_fullquote(s)
    # Now you want the remaining "s to be converted to “s.
    s = s.replace('"','“')
    # Now you want to convert other quotemarks:
    s = s.replace(',,','„')
    s = s.replace("''","”")
    return s

def worthypart_utf(s):
    '''Replaces various "junk" UTF-8 caracters.'''
    s = s.replace('\ufeff', '')
    return s
        