import re
from math import ceil

from gntools.lists import ensure_index

#dependency: PyHyphen
from hyphen import Hyphenator, dict_info

from gntools.texts.utf import worthypart_utf
from gntools.lists import intersection_of_two_lists


### test import
import random

# TODO: Later we want to implement paragraph blocks and get rid or these
PARAGRAPH_MAXINDENT = 8
PARAGRAPH_BODYINDENT = 0
HUGE_VALUE = 10000

# temporary constant for Hyphenation allowed
HYPH = False
lang = 'en_GB'
HEADERS = ['chapter']

class EmptyLineForBlockError(ValueError): pass


class Block():
    # loc: tuple of start and end line number (st, en)
    # loc = (-1,0) is for the first block containing the empty lines at
    #     the beginning of the document in its self.emptyafter 
    def __init__(self, loc, emptyafter, l_lines=None):
        self.loc = loc
        self.emptyafter = emptyafter
        self.l_lines = l_lines

        self.raw_content = ' '.join(self.l_lines)

    def leftmargin(self):
        '''Returns the column number of the left margin'''
        m = HUGE_VALUE
        for i in self.l_lines:
            m = min(m,len(i) - len(i.lstrip()))
        return m

    def rightmargin(self):
        '''Returns the column number of the left margin'''
        m = 0
        for i in self.l_lines:
            m = max(m,len(i))
        return m

    def centered_at(self):
        '''Returns the rightmargin value where 
        the Block would be centered.'''
        # example "...b" returns {7}
        #         "...bl" returns {7,8}
        c_i = set()
        for i in self.l_lines:
            c_ii = set() 
            m = len(i) - len(i.lstrip())
            l_l = len(i.strip())
            
            if l_l % 2 == 0:
                # if content length is even value
                c_ii.add(l_l + 2*m -1)
            else:
                c_ii.add(l_l + 2*m +1)
            c_ii.add(l_l + 2*m)

            if not c_i:
                c_i = c_ii
            else:
                c_i = c_i & c_ii

        return c_i

    def type(self, margin=None):
        '''Returns the type of the block'''
        if len(self.l_lines) == 1:

            for i in HEADERS:
                if self.raw_content.lower().find(i) > -1:
                    return i

        return 'paragraph'
 
    def typetest(self, margin=None):
        print(len(self.l_lines), margin, self.centered_at())
    

def ll_blocks(text):
    '''Generates a linked list of blocks and returns the last one.
    A block is separated by a newline from another.'''
        
    def get_block(i):
        '''Returns the Block starting from line index <i>.'''

        def count_empty(i):
            '''Counts empty lines form a location.
            If location is not empty, return 0.'''
            c = 0
            # here this function uses its parent variable <l>
            while not l[i+c]:
                c += 1
            return c
        
        if i == 0:
            c_e = count_empty(i)
            if c_e:
                return Block((-1,0), c_e, l_lines=[''])
                i = c_e
            return Block((-1,0), 0, l_lines=[''])
        
        # here this function uses its parent variable <l>
        if not l[i]:
            raise EmptyLineForBlockError('Start line of a Block must be nonempty: l{0}.'.format(i+1))

        j = i
        # first we deal with nonempty lines
        while l[j] and j < len(l) - 1:
            j += 1

        # now the empty lines following the block
        c_e = count_empty(j)

        if j == len(l) - 1:
            j += 1

        return Block((i+1,j), c_e, l_lines=l[i:j])

         
    l = text.splitlines()

    first_block = None
    last_block = None

    i = 0
    while i < len(l) - 1:
        block = get_block(i)
        
        if not first_block:
            first_block = block
            block.prev = None
            block.next = None
            last_block = block
        else:
            last_block.next = block
            block.prev = last_block
            block.next = None
            last_block = block

        i = block.loc[1] + block.emptyafter
    
    return first_block

def wrapmargin(first_block):
    '''Detects the wrap margin of a given text.'''
# This is damn slow yet.
#   return max([len(l) for l in text.splitlines()])
    a = []
    x = first_block.next
    while x.next:
        m = x.rightmargin()
        ensure_index(m, a, val=0)
        a[m] += 1
        x = x.next

    return a.index(max(a))




if __name__ == '__main__':
    pass