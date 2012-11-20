import random
#import re
from math import ceil
#dependency: PyHyphen
from hyphen import Hyphenator, dict_info

from gntools.texts.utf import worthypart_utf
from gntools.lists import ensure_index, intersection_of_two_lists

from core.args import args
from core.meta import base_constants

# TODO: Later we want to implement paragraph blocks and get rid or these
PARAGRAPH_MAXINDENT = 8
PARAGRAPH_BODYINDENT = 0
HUGE_VALUE = 10000
MAX_INDENT = 8

# temporary constant for Hyphenation allowed
HEADERS = ['chapter']
BY = 'by'

class EmptyLineForBlockError(ValueError): pass

class Block():
    # loc: tuple of start and end line number (st, en)
    # loc = (-1,0) is for the first block containing the empty lines at
    #     the beginning of the document in its self.emptyafter
    def __init__(self, loc, emptyafter, l_lines=None):
        self.loc = loc
        self.emptyafter = emptyafter
        self.l_lines = l_lines

        self.prev = None
        self.next = None
        self.dlink = None
        self.ulink = None
        self.llink = None
        self.rlink = None

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

        def byed(block):
            '''Return True if a block raw_content has by at the beginning'''
            if block.raw_content().lower().find(base_constants['by']) == 0:
                return True
            return False

        def header(block):
            '''Returns header if header type in content'''
            for i in HEADERS:
                if block.raw_content().lower().find(base_constants[i]) > -1:
                    return i
            return False

        def nr(block):
            '''Returns block number for the first three blocks'''
            if not self.prev:
                return None
            elif not self.prev.prev:
                return 1
            elif not self.prev.prev.prev:
                return 2
            elif not self.prev.prev.prev.prev:
                return 3
            return None

        if len(self.l_lines) == 1:

            header = header(self)
            nr = nr(self)

            if nr == 1:
                if byed(self.next) or byed(self.next.next):
                    return 'title'
                else:
                    return 'author'
            elif nr == 2:
                if byed(self):
                    return 'author'
                elif self.prev.type() == 'author':
                    return 'title'
                elif self.prev.type() == 'title':
                    return 'subtitle'
            elif nr == 3:
                if byed(self):
                    return 'author'
                elif self.prev.type() == 'title' and not header:
                    return 'subtitle'

            if self.raw_content() == '***':
                return 'asterism'

            if header:
                return header

        return 'paragraph'

    def raw_content(self):
        c = ' '.join(self.l_lines)
        c = c.replace('\u2010 ','') # remove hyphens
        while c.find('  ') > -1:
            c = c.replace('  ',' ') # trim double spaces
        return c.strip()

    def join_subblocks(self):
        '''Joins subblocks to the main linked list of blocks'''
        def indents():
            '''Returns the line indices in l_lines which are indented'''
            # for more sophisticated method we can check if line is longer than margin and ensure zero identification in next line
            result = []
            for i in range(len(self.l_lines)):
                l = self.l_lines[i]
                if (0 < len(l) - len(l.lstrip()) <= MAX_INDENT):
                    result.append(i)
            return result
        '''Function to split indented blocks'''

        indices = indents()
        try:
            if indices[0] != 0:
                indices.insert(0,0) # we ensure we start from the beginning
        except:
            return None

        prev_subblock = None
        for i in range(len(indices)):
            st_i = indices[i]
            last = False
            try:
                en_i = indices[i+1]
            except:
                en_i = len(self.l_lines)
                last = True

            subblock = Block((self.loc[0] + st_i + 1, self.loc[0] + en_i), self.emptyafter*last, l_lines=self.l_lines[st_i:en_i])

            if not prev_subblock: # ergo it will be the first one

                self.prev.next = subblock # this gonna join it to the main blocks
                subblock.prev = self.prev
                first_subblock = subblock
            else:
                prev_subblock.next = subblock
                subblock.prev = prev_subblock

            prev_subblock = subblock

            if last: #for last subblock
                subblock.next = self.next
                subblock.emptyafter = self.emptyafter
                if self.next:
                    self.next.prev = subblock # this gonna join it to the main blocks

def ll_blocks(text):
    '''Generates a linked list of blocks and returns the last one.
    A block is separated by a newline from another.'''

    def count_empty(i):
        '''Counts empty lines form a location.
        If location is not empty, return 0.'''
        c = 0
        # here this function uses its parent variable <l>
        while not l[i+c] or l[i+c] == '\ufeff':
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
    last_block = first_block
    i += c_e

    while i < len(l) - 1:
        block = get_block(i)

        last_block.next = block
        block.prev = last_block
        last_block = block

        i = block.loc[1] + block.emptyafter

    block = first_block
    while block.next:
        block.join_subblocks()
        block = block.next
    block.join_subblocks()

    return first_block

def tree_struct(first_block):
    '''Creates a tree of the structural elements of the documents.
    dlink points to the first element of the sublist; ulink for opposite.
    rlink points to the next element of the same level; llink for previous element.'''

    ### Right now, only for chapters
    b = first_block
    prev_b = None
    while b.next:
        if b.type() == 'chapter':
            if prev_b:
                prev_b.rlink = b
                b.llink = prev_b
            else:
                first_block.dlink = b
                b.ulink = first_block
            prev_b = b
        b = b.next

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