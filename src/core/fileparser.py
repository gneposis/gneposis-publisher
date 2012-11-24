import random
#import re
from math import ceil
#dependency: PyHyphen
from hyphen import Hyphenator, dict_info

from gntools.texts.utf import worthypart_utf
from gntools.lists import ensure_index, intersection_of_two_lists

from core.args import args
from core.blocks import *

# TODO: Later we want to implement paragraph blocks and get rid or these
PARAGRAPH_MAXINDENT = 8
PARAGRAPH_BODYINDENT = 0
MAX_INDENT = 8

BY = 'by'

class EmptyLineForBlockError(ValueError): pass

def get_blocks(text, margin=args.M):
    '''Generates a linked list of blocks and returns the first one.
    A block is separated by a newline from another.'''

    def count_empty(i):
        '''Counts empty lines form a location.
        If location is not empty, return 0.'''
        c = 0
        # here this function uses its parent variable <l>
        while not l[i+c] or l[i+c] == '\ufeff':
            c += 1
        return c

    def get_raw_block(i):
        '''Returns the location of nonempty lines from a given index.'''

        # here this function uses its parent variable <l>
        if not l[i]:
            raise EmptyLineForBlockError('Start line of a Block must be nonempty: l{0}.'.format(i+1))

        j = i
        # first we deal with nonempty lines
        while l[j] and j < len(l) - 1:
            j += 1

        # now the empty lines following the block
        c_e = count_empty(j)

        # in case we reached end of document
        if j == len(l) - 1:
            j += 1

        #return Block((i,j), c_e, l_lines=l[i:j])
        return j, c_e

    def subblocks(l_lines):
        '''Joins subblocks to the main linked list of blocks'''

        def indents():
            '''Returns the line indices in l_lines which are indented'''
            # for more sophisticated method we can check if line is longer than margin and ensure zero identification in next line
            result = []
            for i in range(len(l_lines)):
                l = l_lines[i]
                if (0 < len(l) - len(l.lstrip()) <= MAX_INDENT):
                    result.append(i)
            return result
        '''Function to split indented blocks'''

        indices = indents()
        result = []

        # return the whole l_lines if there is no indented lines
        try:
            if indices[0] != 0:
                indices.insert(0,0) # we ensure we start from the beginning
        except:
            result.append(l_lines)
            return result

        # append subblocks
        for i in range(len(indices)):
            st_i = indices[i]
            try:
                en_i = indices[i+1]
            except:
                en_i = len(l_lines)
            result.append(l_lines[st_i:en_i])

        return result

    l = text.splitlines()
    i = 0
    c_e = count_empty(i)

    #we initialize document header which stores the count of empty lines at the beginning of text
    first_block = DocumentHeader(c_e)

    last_block = first_block
    i += c_e
    n = 1

    while i < len(l) - 1:                              # until end of document
        b_loc = get_raw_block(i)                       # we separate raw blocks (separated by empty lines)
        l_lines = l[i:b_loc[0]]                        # we get the line content for them
        l_blocks = subblocks(l_lines)                  # we divide them by subblocks (if any) -- this is for indented paragraphs with no empty line between each other
        while l_blocks:                                # while we have subblock remained
            block = get_block(l_blocks.pop(0), margin) # we create blok from the populated first
            n += 1                                     # we increase block counter
            last_block.next = block                    # link
            block.prev = last_block                    # link
            last_block = block                         # now we have a new last block
        last_block.emptyafter = b_loc[1]               # the very last one inherits the emptyafter of the raw_block
        i = b_loc[0] + b_loc[1]                        # our new line index value

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

if __name__ == '__main__':
    pass