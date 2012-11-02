import random
from hyphen import Hyphenator, dict_info

from gntools.lists import nth

class OutOfMarginError(ValueError): pass
class UnavailableHyphDictionaryError(ValueError): pass

PRIOR_BREAK_CHARS = {'.', ',', ':', ';'}
JUSTIFY_METHODS = {'deep', 'rand', 'left'}

def reform_par(text, lang, indent=0, justify=None, margin=72):
    '''Reformats a paragraph, using hyphenation if hyph is True.
    Justifies it if justify = "deep", "rand" or "left".
    Justify methods:
        "deep" is the most precise but slow
        "rand" is pure random
        "left" is adding spaces from left side
    '''

    def cut_string(string, lang=lang, margin=margin):
        '''Cut a string at a breakpoint (whitespace) before margin.
        Hyphenates if lang is in the available dictionaries.
        Returns a list of three elements:
            [0]: The result line of text
            [1]: The index of starting point of the next line in string
            [2]: The remained part of hyphenated word plus a whitespace or '' if none
        '''
        break_before_margin = string[:margin].rfind(' ')
        
        if lang in dict_info.keys():
            break_after_margin = string[margin:].find(' ')
            
            if not break_after_margin:
                word_at_break = None
                word_hyphenated = None
            else:
                word_at_break = string[break_before_margin + 1 : margin + break_after_margin]
                word_hyphenated = Hyphenator(lang).wrap(word_at_break, margin - break_before_margin - 1)
            
            if word_hyphenated:
                return string[:break_before_margin + 1] + word_hyphenated[0], margin + break_after_margin + 1, word_hyphenated[1] + ' '
            elif word_at_break:
                return string[:break_before_margin], break_before_margin + 1, ''
            else:
                return string[:margin], margin + 1, ''
        elif lang:
            raise UnavailableHyphDictionaryError('Hyphenation dictionary for language {0} is not available. Please install it first.'.format(lang))

        return string[:break_before_margin], break_before_margin + 1, ''

    def justify_line(line_of_text, margin=margin, method=justify):
        '''Justifies a line of text.
        Methods:
        "deep" is the most precise but slow
        "rand" is pure random
        "left" is adding spaces from left side
        '''

        def get_priority_breaks(l_line):
            '''Determines the priority break points for deep justify method.'''
            break_count = len(l_line) - 1
            prior_breaks = [False for x in range(break_count)]
            for i in range(break_count):
                if l_line[i][-1] in PRIOR_BREAK_CHARS:
                    prior_breaks[i] = True
            return prior_breaks

        def rand_break(l_break, lookfor=True):
            '''Chooses a break randomly for justifiing'''
            # - first by getting the count of not used yet
            count = sum(1 for x in l_break if x == lookfor)
            # now choose one randomly
            c_i = random.randint(1, count)
            # now we want the index of (c_i)th False in braks_used
            return nth(c_i, l_break, lookfor=lookfor)

        if len(line_of_text) == margin: # If we are lucky, why bother calculating?
            return line_of_text
        elif len(line_of_text) > margin:
            raise OutOfMarginError('Line is longer than margin, use reform_par first.')

        n = margin - len(line_of_text) # Amount of whitespaces we need
        l_line = line_of_text.split()
        break_count = len(l_line) - 1 # Amount of whitespaces we already have
        spaces_breaks = [int((n + break_count) / break_count) for x in range(break_count)]
        m = sum(spaces_breaks) - break_count # New amount of whitespaces we need

        s_i = -1
        breaks_used = [False for x in range(break_count)]

        if method == 'deep': # initiate necessary variables for deep method
            prior_breaks = get_priority_breaks(l_line)
            free_prior_breaks = None

        while 0 < n - m:
            if method == 'deep':
                if prior_breaks > breaks_used: # If we arent used all our prior breaks yet
                    free_prior_breaks = prior_breaks
                    # Now we determine the free prior breaks
                    for b_i in range(len(prior_breaks)):
                        if prior_breaks[b_i] and breaks_used[b_i]:
                            free_prior_breaks[b_i] = False
                    s_i = rand_break(free_prior_breaks)
                    breaks_used[s_i] = True
                else:
                    s_i = rand_break(breaks_used, lookfor=False)
                    breaks_used[s_i] = True
            elif method == 'rand':
                s_i = rand_break(breaks_used, lookfor=False)
                breaks_used[s_i] = True
            elif method == 'left':
                s_i += 1
            else:
                raise IllegalMethod('Illegal method call {0}'.format(justify))

            spaces_breaks[s_i] += 1
            m += 1

            line_of_text = l_line[0]

        for b_i in range(break_count):
            line_of_text += ' '*spaces_breaks[b_i] + l_line[b_i+1] # Now add necessary amount whitespaces + words one-by-one

        return line_of_text
    
    result = []

    in_first_line = True
    in_last_line = False    

    while not in_last_line:

        if len(text) <= margin:
            in_last_line = True
            result.append(text)
            return '\n'.join(result)
        
        x = cut_string(text, margin = margin - in_first_line * indent)
        text = x[2] + text[x[1]:]

        line_of_text = x[0]

        if justify and not in_last_line:
            line_of_text = justify_line(line_of_text, margin = margin - in_first_line * indent)

        if in_first_line:
            line_of_text = ' '*indent + line_of_text
            in_first_line = False

        result.append(line_of_text)

    return '\n'.join(result)
