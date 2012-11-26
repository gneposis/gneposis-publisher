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
        if not block.dlink:
            return block, True
        else:
            block = block.dlink
            while block.rlink:
                block = block.rlink
            return block, False

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
            last_block.next = block            # link
            block.prev = last_block            # link
            last_block = block                 # now we have a new last block
            n += 1                             
        i = b_loc[0] + b_loc[1]                # our new line index value

    # now we gonna create the tree of the blocks
    # for this we need to determine the block hierarchy
        # which we gonna program later :)

    current_position = docheader.frontmatter.titlepage, True
    current_block = docheader.next
    while current_block.next:
        if isinstance(current_block, core.blocks.Chapter): # chapter triggers mainmatter
            current_position = last_link(docheader.mainmatter)
        elif isinstance(current_block, core.blocks.Paragraph): # paragraphs goes below chapters
            current_position = last_link(last_link(docheader.mainmatter)[0]) # only second hierarchy level this time
 
        if current_position[1]:
            current_position[0].dlink = current_block
            current_block.ulink = current_position[0]
        else:
            current_position[0].rlink = current_block            
            current_block.llink = current_position[0]
 
        current_block = current_block.next

    return docheader

if __name__ == '__main__':
    pass




#       def leftmargin():
#           '''Returns the column number of the left margin'''
#           m = HUGE_VALUE
#           for i in l_lines:
#               m = min(m,len(i) - len(i.lstrip()))
#           return m
#   
#       def rightmargin():
#           '''Returns the column number of the left margin'''
#           m = 0
#           for i in l_lines:
#               m = max(m,len(i))
#           return m
#   
#       def centered():
#           '''Returns True if l_lines is centered.'''
#   
#           # At first it calculates the rightmargin value where the Block would be centered.
#           # example "...b" gives {7}
#           #         "...bl" gives {7,8}
#           c_i = set()
#           for i in l_lines:
#               c_ii = set()
#               m = len(i) - len(i.lstrip())
#               l_l = len(i.strip())
#   
#               if l_l % 2 == 0:
#                   # if content length is even value
#                   c_ii.add(l_l + 2*m -1)
#               else:
#                   c_ii.add(l_l + 2*m +1)
#               c_ii.add(l_l + 2*m)
#   
#               if not c_i:
#                   c_i = c_ii
#               else:
#                   c_i = c_i & c_ii
#   
#           if margin in c_i and leftmargin():
#               return True
#           return False
#   
#       def block_is_header(block, _try = False):
#           from core.fileparser import HEADERS
#           if block:
#               if _try:
#                   try:
#                       if block.type() in HEADERS:
#                           return True
#                   except:
#                           return False
#               if block.type() in HEADERS:
#                   return True
#           return False
#   
#       def get_header(content):
#           '''Returns header if header type in content'''
#           for i in HEADERS:
#               if block.raw_content().lower().find(base_constants[i]) > -1:
#                   return i
#           return False