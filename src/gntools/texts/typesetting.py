import random
from hyphen import Hyphenator, dict_info

from gntools.lists import nth

class OutOfMarginError(ValueError): pass

PRIOR_BREAK_CHARS = {'.', ',', ':', ';'}
JUSTIFY_METHODS = {'deep', 'rand', 'left'}

def reform_par(partext, lang, margin=72, hyph=True, indent=0, justify=None):
    '''Reformats a paragraph, using hyphenation if hyph is True.
    Justifies it if justify = "deep", "rand" or "left".
    Justify methods:
        "deep" is the most precise but slow
        "rand" is pure random
        "left" is adding spaces from left side
    '''

    def len_hyph_remained():
        if not hyph_remained:
            return 0
        return len(hyph_remained) + 1

    def get_priority_breaks(l_line):
        '''Determines the priority break points for deep justify method'''
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

    i = 0
    j = 0
    result = []
    hyph_remained = ''
    in_first_line = True

    while j != -1: # j will be the index of the rfinder: -1 means no whitespace was found
        if len(partext) - i <= margin:
            result.append(hyph_remained + partext[i:])
            j = -1          
        else:
            if in_first_line and indent:
                j = partext[ i : i + margin - len_hyph_remained() - indent].rfind(' ') # last space before margin
                t = ' '*indent + hyph_remained + partext[i:i+j]
            else:
                j = partext[ i : i + margin - len_hyph_remained()].rfind(' ') # last space before margin
                t = hyph_remained + partext[i:i+j]
            
            if hyph:
                # now we should check if a hyhenated word fits there
                loc = i + j + 1
                k = partext[loc:].find(' ')
                next_word = partext[loc : loc+k]
                free_space = margin - j - len_hyph_remained() - 1
                hyph_word = Hyphenator(lang).wrap(next_word, free_space)
                if hyph_word:
                    t += ' ' + hyph_word[0]
                    hyph_remained = hyph_word[1]
                    i += k
                else:
                    hyph_remained = ''
            
            if justify in JUSTIFY_METHODS:
                
                if len(t) == margin: # If we are lucky, why bother calculating?
                    pass
                elif len(t) > margin:
                    raise OutOfMarginError('Line is longer than margin, use reform_par first.')
                
                n = margin - len(t) # Amount of whitespaces we need
                l_line = t.split()
                break_count = len(l_line) - 1 # Amount of whitespaces we already have
                spaces_breaks = [int((n + break_count) / break_count) for x in range(break_count)]
                m = sum(spaces_breaks) - break_count # New amount of whitespaces we need
                
                s_i = -1
                breaks_used = [False for x in range(break_count)]
                
                if justify == 'deep': # initiate necessary variables for deep method
                    prior_breaks = get_priority_breaks(l_line)
                    free_prior_breaks = None
                
                while 0 < n - m:
                    if justify == 'deep':
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
                
                    elif justify == 'rand':
                        s_i = rand_break(breaks_used, lookfor=False)
                        breaks_used[s_i] = True
                    elif justify == 'left':   
                        s_i += 1
                    else:
                        raise IllegalMethod('Illegal method call {0}'.format(justify))
                
                    spaces_breaks[s_i] += 1
                    m += 1
                
                if in_first_line and indent:
                    t = ' '*indent + l_line[0] # Add first word
                else:
                    t = l_line[0]
                
                for b_i in range(break_count):
                    t += ' '*spaces_breaks[b_i] + l_line[b_i+1] # Now add necessary amount whitespaces + words one-by-one

            result.append(t)
            in_first_line = False
            i += j + 1

    return '\n'.join(result)
