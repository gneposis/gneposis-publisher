from math import pow

class OutOfRangeError(ValueError): pass
class NotIntegerError(ValueError): pass
class InvalidInputStringError(ValueError): pass
class InvalidSeparatorError(ValueError): pass

DEPTH = 5                
                #0 , 1000  , 1000000 , 1000^3    , 1000^4 ...              
separator_map = ('', 'ezer' , 'millió', 'milliárd', 'billió')
                
          
hu_text_map = ( ('kilencven'    , 90),
                ('nyolcvan'     , 80),
                ('hetven'       , 70),
                ('hatvan'       , 60),
                ('ötven'        , 50),
                ('negyven'      , 40),
                ('harminc'      , 30),
                ('huszonkilenc' , 29),
                ('huszonnyolc'  , 28),
                ('huszonhét'    , 27),
                ('huszonhat'    , 26),
                ('huszonöt'     , 25),
                ('huszonnégy'   , 24),
                ('huszonhárom'  , 23),
                ('huszonkettő'  , 22),
                ('huszonegy'    , 21),
                ('húsz'         , 20),
                ('tizenkilenc'  , 19),
                ('tizennyolc'   , 18),
                ('tizenhét'     , 17),
                ('tizenhat'     , 16),
                ('tizenöt'      , 15),
                ('tizennégy'    , 14),
                ('tizenhárom'   , 13),
                ('tizenkettő'   , 12),
                ('tizenegy'     , 11),
                ('tíz'          , 10),
                ('kilenc'       ,  9),
                ('nyolc'        ,  8),
                ('hét'          ,  7),
                ('hat'          ,  6),
                ('öt'           ,  5),
                ('négy'         ,  4),
                ('három'        ,  3),
                ('kettő'        ,  2),
                ('egy'          ,  1))

def to_text(n):
    '''convert integer to hungarian text'''
    
    def textize(n, loc=0):
        '''convert 0 < n < 1000 to hungarian text'''
        
        if not isinstance(n, int):
            raise NotIntegerError('non-integers can not be converted')
        
        if loc == 0 and not (0 < n < 2000):
            raise OutOfRangeError('number for textize function must between 0 and 2000 if first index')
        elif loc > 0 and not (0 < n < 1000):
            raise OutOfRangeError('number for textize function must between 0 and 1000 if not first index')       
    
        def thousands(n):
            if loc == 0 and n >= 1000:
                m = n - 1000
                return (m, 'ezer')
            return (n, '')
    
        def hundreds(n):
            for text, integer in hu_text_map[27:]:
                if n >= integer * 100:
                    m = n - integer * 100
                    if text == 'kettő':
                        text = 'két'
                    elif text == 'egy' and x == n:
                        text = ''
                    return (m, text + 'száz')
            return (n, '')
    
        def from90to30(n):
            for text, integer in hu_text_map[:7]:
                if n >= integer:
                    m = n - integer
                    return (m, text)
            return (n, '')
    
        def from29to1(n):
            for text, integer in hu_text_map[7:]:
                if n >= integer:
                    m = n - integer
                    if text[-5:] == 'kettő' and loc>0:
                        text = text[:-5] + 'két'
                    return (m, text)
            return (n, '')
        
        x = n
        
        result = ''
        
        r = thousands(n)
        m = r[0]
        result = result + r[1]
        r = hundreds(m)
        m = r[0]
        result = result + r[1]
        r = from90to30(m)
        m = r[0]
        result = result + r[1]
        r = from29to1(m)
        m = r[0]
        result = result + r[1]
         
        return result
    
    def slicer(n):
        '''slices the integer by power of thousends'''
        # You want to convert the integer to string and reverse it
        n = str(n)[::-1]
        result = []
        for i in range(DEPTH):
            # You want to slice the string by 3 characters and reverse the result
            nr = n[3*i:3*i+3][::-1]
            if nr == '':
                nr = 0
            nr = int(nr)
            result.insert(0, nr)
        
        if result[-2] == 1:
            result[-2] = 0
            result[-1] = 1000 + result[-1]
    
        return tuple(result)
    
    def postprocess(resulttuple):
        result = ''.join(resulttuple)
        if result[:5] == 'ezer-':
            result = 'ezer' + result[5:]
        if result[-1] == '-':
            result = result[:-1]
        if minus:
            result = 'mínusz ' + result
        return result
    
    if not isinstance(n, int):
        raise NotIntegerError('non-integers can not be converted')

    if not (-1000000000000000 < n < 1000000000000000):
        raise OutOfRangeError('number out of range (abs must be less than 1000000000000000)')

    if n < 0:
        minus = True
        n = abs(n)
    else:
        minus = False

    if n == 0:
        return 'nulla'
    
    result = ['']*DEPTH
    for i in range(DEPTH):
        if slicer(n)[i] > 0:
            location = DEPTH-i-1
            if location > 0:
                dash = '-'
            else:
                dash = ''
            text = textize(slicer(n)[i], loc=location) + separator_map[-i-1] + dash
            result[i] = text

    return postprocess(result)

def from_text(text):
    '''convert integer to hungarian text'''
    
    def integerize(s, loc=0):
        '''convert valid hungarian text to 0 < n < 1000 integer'''      
        
        def thousands(s):
            if loc == 0 and s[:4] == 'ezer':
                return (1000, s[4:])
            return (0, s)
        
        def hundreds(n, s):
            for text, integer in hu_text_map[27:]:
                if text == 'kettő':
                    text = 'két'
                elif text == 'egy' and s == string:
                    text = ''
                if s[:len(text) + 4] == text + 'száz':
                    return (n + integer * 100, s[len(text) + 4:])
            return (n, s)
        
        def from90to30(n, s):
            for text, integer in hu_text_map[:7]:
                if s[:len(text)] == text:
                    return (n + integer, s[len(text):])
            return (n, s)
        
        def from29to1(n, s):
            for text, integer in hu_text_map[7:]:
                if text[-5:] == 'kettő' and loc>0:
                    text = text[:-5] + 'két'
                if s[:len(text)] == text:
                    return (n + integer, s[len(text):])
            return (n, s)
        
        string = s
        
        result = thousands(s)
        result = hundreds(result[0], result[1])
        result = from90to30(result[0], result[1])
        result = from29to1(result[0], result[1])
        return result
    
    def check_separator(s):
        '''returns power of 1000 by separator text'''
        for i in range(len(separator_map)):
            if s == separator_map[i]:
                return i
        raise InvalidSeparatorError('not valid separator')
    
    def verify(l):
        raiseit = False
        try:
            if l[1] == 'ezer':
                raiseit = True
        except:
            return None
        if raiseit:
            raise InvalidInputStringError('not valid input')
    
    if text == 'nulla':
        return 0
    
    if text[:7] == 'mínusz ':
        minus = True
        text = text[7:]
    else:
        minus = False
    
    text_list = text.split('-')
    text_list.reverse()
    
    verify(text_list)
    
    result = 0
    texind = 0
    sepind = 0
    
    while texind < len(text_list):
        try:
            result += integerize(text_list[texind],sepind)[0] * pow(1000, check_separator(integerize(text_list[texind],sepind)[1]))
            sepind = check_separator(integerize(text_list[texind],sepind)[1])
            texind += 1
        except:
            sepind += 1
    
    if minus:
        result = -int(result)
    else:
        result = int(result)
                                     
    return result

hu_ord_map = (('billió', 'billiomodik'),
              ('milliárd', 'milliárdodik'),
              ('millió', 'milliomodik'),
              ('ezer', 'ezredik'),
              ('száz', 'századik'),
              ('kilencven', 'kilencvenedik'),
              ('nyolcvan', 'nyolcvanadik'),
              ('hetven', 'hetvenedik'),
              ('hatvan', 'hatvanadik'),
              ('ötven', 'ötvenedik'),
              ('negyven', 'negyvenedik'),
              ('harminc', 'harmincadik'),
              ('húsz', 'huszadik'),
              ('tíz', 'tizedik'),
              ('kilenc', 'kilencedik'),
              ('nyolc', 'nyolcadik'),
              ('hét', 'hetedik'),
              ('hat', 'hatodik'),
              ('öt', 'ötödik'),
              ('négy', 'negyedik'),
              ('három', 'harmadik'),
              ('kettő', 'kettedik'),
              ('egy', 'egyedik'))

def to_text_ord(n):
    if n == 0:
        return 'nulladik'
    elif n == 1:
        return 'első'
    elif n == 2:
        return 'második'
    else:
        text = to_text(n)
        for search, replace in hu_ord_map:
            if text[-len(search):] == search:
                return text[:-len(search)] + replace