import re
from math import ceil

#dependency: PyHyphen
from hyphen import Hyphenator, dict_info

from gntools.texts.utf import worthypart_utf
from gntools.lists import intersection_of_two_lists


### test import
import random

# TODO: Later we want to implement paragraph blocks and get rid or these
PARAGRAPH_MAXINDENT = 8
PARAGRAPH_BODYINDENT = 0

# temporary constant for Hyphenation allowed
HYPH = False
lang = 'en_GB'

#temporary for wrapmargin
WRAPMARGIN_BARRIER = 0.05

class InvalidLineNumberError(ValueError): pass
class NoMarginError(ValueError): pass

class Line():
    def __init__(self, s, margin=None):

        self.fullcont = s
        self.margin = margin
        self.cont = self.fullcont.strip()
        self.length = len(self.cont)
        
        if not worthypart_utf(self.cont):
            self.empty = True
        else:
            self.empty = False

    # generates tuple of (leftindent, shiftfromcenter, -rightindent)
    def indent(self):
            if not self.margin:
                raise NoMarginError('No margin value!')
            elif self.empty:
                return None
            else:
                temp_fullcontent = worthypart_utf(self.fullcont)
                leftindent = len(temp_fullcontent) - len(self.fullcont.lstrip())
                rightindent = len(temp_fullcontent.rstrip()) - self.margin
                centerindent = ceil((leftindent + rightindent)/2)
                return [leftindent, centerindent, rightindent]
    
    def rawcont(self):
        '''Generates the raw content of self.cont'''
        return self.cont

    def space(self, rightside=True):
        '''Determines the empty space in the line.
        If rightside=True then space before the content doesn't count.'''
        if rightside:
            return self.margin - self.length
        return self.margin - len(self.fullcont)

    def firstwrap(self, hyph=HYPH):
        '''Determines the length of first wrap.
        We use this to determine if line was wrapped at the last
        possible place or not
        '''
        
        try:
            firstword = self.cont.split()[0]
        except:
            return 0

        if not hyph:
            return len(firstword)
        
        h = Hyphenator(lang)
        i = 1
        while not h.wrap(firstword, i) and i < len(firstword):
            i += 1
        return i

            
class Block():
    # loc: tuple of start and end line number (st, en)
    # loc = (-1,0) is for the first block containing the empty lines at
    #     the beginning of the document in its self.emptyafter 
    def __init__(self, loc, l_lines, indent, emptyafter=0, indented=None):
        self.loc = loc
        self.l_lines = l_lines
        self.emptyafter = emptyafter
        self.indented = indented
        self.indent = indent

    def cont(self):
        c = []
        for i in self.l_lines:
            c.append(i.cont)
        return ' '.join(c)

    # style set for blocks
    def style(self):
        s = set()

        # centered
        if self.indent and self.indent[1] == 0:
            s.add('centered')

        return s


    def reformat(self):
        pass

def l_lines(text):
    wm = wrapmargin(text)
    t = text.splitlines()

    l = []    
    for i in t:
        l.append(Line(i, wm))
    
    return l

def ll_blocks(text):
    '''Generates a linked list of blocks and returns the last one'''
    
    def get_block(start_line, l): # l is the output of l_lines(text)

        def compare_values(first, second):
            if first == second:
                return first
            return None
        
        def get_lines_list():
            pass
        
        i = 0
        count_empty = 0
        block_indent = None
        indented = None
        last_space = 0 # empty space in the last line
        
        if start_line > len(l):
            raise InvalidLineNumberError('Too high line number: {0} not in document. Valid line numbers: 0 ... {1}'.format(start_line, len(lines)))
        elif start_line == 0:
            while l[start_line + i].empty:
                count_empty += 1
                i += 1
            return Block((-1,0), None, None, emptyafter=count_empty)
        
        while start_line -1 + i < len(l):
            pos = start_line -1 + i
            current_indent = l[pos].indent()
            #print(pos, current_indent)
        
            # if start_line is empty go to next line
            if l[pos].empty and not block_indent:
                last_space = 0
                start_line += 1
        
            # now we are at the beginning of a block 
            elif not l[pos].empty and not block_indent:
                block_indent = current_indent
                last_space = l[pos].space()
                i += 1
            
            # now we are inside the block and not at the beginning of the next
            elif (not l[pos].empty 
                    and block_indent
                    and count_empty == 0 
                    and intersection_of_two_lists(block_indent, current_indent)
                    and last_space <= l[pos].firstwrap()
                 ):
                block_indent =  intersection_of_two_lists(block_indent, current_indent)
                last_space = l[pos].space()
                i += 1
        
            # we encountered an indented paragraph
            elif (not l[pos].empty 
                    and block_indent
                    and count_empty == 0 
                    and (PARAGRAPH_BODYINDENT == current_indent[0] < block_indent[0] <= PARAGRAPH_MAXINDENT)
                    and last_space <= l[pos].firstwrap()
                 ):
                indented = block_indent[0] - current_indent[0]
                block_indent[0] = current_indent[0]
                block_indent[1] = compare_values(block_indent[1], current_indent[1])
                block_indent[2] = compare_values(block_indent[2], current_indent[2])
                last_space = l[pos].space()
                i += 1
        
            # we are at the beginning of the next block which immediately followed this one
            elif (not l[pos].empty
                    and block_indent
                    and count_empty == 0
                    and ( not intersection_of_two_lists(block_indent, current_indent)
                            or last_space > l[pos].firstwrap() )
                 ):
                return Block((start_line, start_line + i - 1), l[start_line -1 : start_line + i - 1], block_indent, emptyafter=0, indented=indented)
        
            # empty lines after block
            elif l[pos].empty and block_indent:
                count_empty += 1
                last_space = 0
                i += 1
        
            # now we are at the beginning of the next block
            else:
                return Block((start_line, start_line + i - count_empty - 1), l[start_line - 1 : start_line + i - count_empty - 1], block_indent, emptyafter=count_empty, indented=indented)
        
        # now after while loop exit we reached the end of document
        return Block((start_line, start_line + i - count_empty - 1), l[start_line - 1 : start_line + i - count_empty - 1], block_indent, emptyafter=count_empty, indented=indented)


    l = l_lines(text)

    first_block = None
    last_block = None
    
    i = 0
    while i <= len(l):
        block = get_block(i, l)
        
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

        i = block.loc[1] + block.emptyafter + 1
    
    return first_block

def wrapmargin(text):
    '''Detects the wrap margin of a given text.
    This function will try to detect the wrapmargin even if longer lines
    are present.
    '''
    distribution = {}
    wrapmargin = None

    l_text = text.splitlines()

    for l in l_text:
        try:
            distribution[len(l)] += 1
        except:
            distribution[len(l)] = 1

    for i in distribution:
        if distribution[i] > len(l_text) * WRAPMARGIN_BARRIER:
            wrapmargin = i

    return wrapmargin
#    return max([len(l) for l in text.splitlines()])




if __name__ == '__main__':
    pass