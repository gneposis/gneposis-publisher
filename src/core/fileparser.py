import random
#import re
from math import ceil
#dependency: PyHyphen
from hyphen import Hyphenator, dict_info

from gntools.texts.utf import worthypart_utf
from gntools.lists import ensure_index, intersection_of_two_lists

from core.args import args
from core.meta import base_constants
import core.blocks

# TODO: Later we want to implement paragraph blocks and get rid or these
PARAGRAPH_MAXINDENT = 8
PARAGRAPH_BODYINDENT = 0
MAX_INDENT = 8

BY = 'by'

class EmptyLineForBlockError(ValueError): pass

def get_blocks(text, margin=args.M, verbose=False):
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

    def get_block(l_lines):
        if len(l_lines) == 1:
            if n == 1: # first block must be the author
                return core.blocks.Author(l_lines, emptyafter)
            elif n == 2: # second block must be the title
                return core.blocks.Title(l_lines, emptyafter)
            elif n == 3 and last_block.emptyafter == 0: # subtitle must be in the very next line of title
                return core.blocks.SubTitle(l_lines, emptyafter)

            elif l_lines[0].lower().find(base_constants['chapter']) > -1:
                return core.blocks.Chapter(l_lines, emptyafter)

            elif l_lines[0].strip() == '***':
                return core.blocks.Break(l_lines, emptyafter)

        return core.blocks.Paragraph(l_lines, emptyafter)

    def last_link(block):
        block = block.dlink
        while block.rlink:
            block = block.rlink
        return block

    if verbose:
        print('Parsing input file:',end='\n\n')

    l = text.splitlines()
    i = 0
    c_e = count_empty(i)

    #we initialize document header which stores the count of empty lines at the beginning of text
    docheader = core.blocks.DocumentHeader(c_e)

    last_block = docheader
    i += c_e
    n = 1

    while i < len(l) - 1:                      # until end of document
        b_loc = get_raw_block(i)               # we separate raw blocks (separated by empty lines)
        l_lines = l[i:b_loc[0]]                # we get the line content for them
        l_blocks = subblocks(l_lines)          # we divide them by subblocks (if any) -- this is for indented paragraphs with no empty line between each other
        while l_blocks:                        # while we have subblock remained
            if len(l_blocks) == 1:
                emptyafter = b_loc[1]          # last one inherits raw_blocks emptyafter
            else:
                emptyafter = 0                 # otherwise zero empty line after the block
            block = get_block(l_blocks.pop(0)) # we create block from the populated first
            if verbose:
                from gntools.filepath import writeout
                writeout('Recognizing blocks: '+str(n), False, replace_lines=1)

            last_block.next = block            # link
            block.prev = last_block            # link
            last_block = block                 # now we have a new last block
            n += 1
        i = b_loc[0] + b_loc[1]                # our new line index value

    if verbose:
        print(' ... done.')
        print('Parsing block hierarchy ... ', end='')

    # now we gonna create the tree of the blocks
    # for this we need to determine the block hierarchy
        # which we gonna program later :)

    current_position = [docheader.frontmatter.titlepage]
    current_block = docheader.next
    while current_block.next:

        if isinstance(current_block, core.blocks.Chapter): # chapter triggers mainmatter
            current_position = [docheader.mainmatter]

        if not current_position[-1].dlink:
            current_position[-1].dlink = current_block
            current_block.ulink = current_position[-1]
        else:
            current_block.llink = last_link(current_position[-1]) # this must be first
            last_link(current_position[-1]).rlink = current_block

        if isinstance(current_block, core.blocks.Chapter): # chapter gets to the end of current position
            current_position.append(current_block)

        current_block = current_block.next

    current_block.llink = last_link(current_position[-1]) # this must be first
    last_link(current_position[-1]).rlink = current_block

    if verbose:
        print('done.')

    return docheader

if __name__ == '__main__':
    pass