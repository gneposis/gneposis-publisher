import re
from math import ceil

from core.args import args

from gntools.lists import ensure_index

#dependency: PyHyphen
from hyphen import Hyphenator, dict_info

from gntools.debug import log
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

def ll_blocks(text):
    '''Generates a linked list of blocks and returns the last one.
    A block is separated by a newline from another.'''

    def count_empty(i):
        '''Counts empty lines form a location.
        If location is not empty, return 0.'''
        c = 0
        # here this function uses its parent variable <l>
        while not l[i+c]:
            c += 1
        return c
        
    def get_block(i):
        '''Returns the Block starting from line index <i>.'''
        
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

        #log(' '.join(l[i:j])+'\n', False)
        return Block((i,j), c_e, l_lines=l[i:j])

         
    l = text.splitlines()
    i = 0

    c_e = count_empty(i)
    
    # first block is always only to store empty lines at the beginning of text
    first_block = Block((-1,0), c_e, l_lines=[''])
    first_block.prev = None
    first_block.next = None
    last_block = first_block
    i += c_e

    while i < len(l) - 1:
    
        log(str(args.stline + i)+' ')

        block = get_block(i)

        last_block.next = block
        block.prev = last_block
        block.next = None
        last_block = block
    
        i = block.loc[1] + block.emptyafter
           
    return first_block

def wrapmargin(first_block):
    '''Detects the wrap margin of a given text.'''

    def add_margin():
        m = x.rightmargin()
        ensure_index(m, a, val=0)
        a[m] += 1
        
    a = []
    x = first_block.next

    while x.next:
        add_margin()
        x = x.next
    add_margin()

    return a.index(max(a))




if __name__ == '__main__':
    pass