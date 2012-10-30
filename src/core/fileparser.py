import re
from math import ceil

from gntools.textform import worthypart_utf
from gntools.lists import intersection_of_two_lists

# TODO: Later we want to implement paragraph blocks and get rid or these
PARAGRAPH_MAXINDENT = 8
PARAGRAPH_BODYINDENT = 0

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

class Block():
    # lines: tuple of start and end line number (st, en)
    # lines = (-1,-1) is for the first block containing the empty lines at
    #     the beginning of the document in its self.emptyafter 
    def __init__(self, lines, indent, emptyafter=0, indented=None):
        self.lines = lines
        self.emptyafter = emptyafter
        self.indented = indented
        self.indent = indent

    # l is the output of lines(text)
    def content(self, l):
        # if lines = (-1,-1)
        if self.lines == (-1, -1):
            return None

        content = []
        for i in range(self.lines[0]-1,self.lines[1]):
            if not l[i].empty:
                content.append(l[i].cont)
        return ' '.join(content)

    # style set for blocks
    def style(self):
        s = set()

        # centered
        if self.indent and self.indent[1] == 0:
            s.add('centered')

        return s

def wrapmargin(text):
    return max([len(l) for l in text.splitlines()])

def lines(text):
    wm = wrapmargin(text)
    t = text.splitlines()

    l = []    
    for i in t:
        l.append(Line(i, wm))
    
    return l

# l is the output of lines(text)
def get_block(start_line, l):

    def compare_values(first, second):
        if first == second:
            return first
        return None

    i = 0
    count_empty = 0
    block_indent = None
    indented = None

    if start_line > len(l):
        raise InvalidLineNumberError('Too high line number: {0} not in document. Valid line numbers: 0 ... {1}'.format(start_line, len(lines)))
    elif start_line == 0:
        while l[start_line + i].empty:
            count_empty += 1
            i += 1
        return Block((-1,-1), None, emptyafter=count_empty)

    while start_line -1 + i < len(l):
        pos = start_line -1 + i
        current_indent = l[pos].indent()
        #print(pos, current_indent)

        # if start_line is empty go to next line
        if l[pos].empty and not block_indent:
            start_line += 1

        # now we are at the beginning of a block 
        elif not l[pos].empty and not block_indent:
            block_indent = current_indent
            i += 1
        
        # now we are inside the block and not at the beginning of the next
        elif not l[pos].empty and block_indent and count_empty == 0 and intersection_of_two_lists(block_indent, current_indent):
            block_indent =  intersection_of_two_lists(block_indent, current_indent)
            i += 1

        # we encountered an indented paragraph
        elif not l[pos].empty and block_indent and count_empty == 0 and (PARAGRAPH_BODYINDENT == current_indent[0] < block_indent[0] <= PARAGRAPH_MAXINDENT):
            indented = block_indent[0] - current_indent[0]
            block_indent[0] = current_indent[0]
            block_indent[1] = compare_values(block_indent[1], current_indent[1])
            block_indent[2] = compare_values(block_indent[2], current_indent[2])
            i += 1

        # we are at the beginning of the next block which immediately followed this one
        elif not l[pos].empty and block_indent and count_empty == 0 and not intersection_of_two_lists(block_indent, current_indent):
            return Block((start_line, start_line + i - 1), block_indent, emptyafter=0, indented=indented)

        # empty lines after block
        elif l[pos].empty and block_indent:
            count_empty += 1
            i += 1

        # now we are at the beginning of the next block
        else:
            return Block((start_line, start_line + i - count_empty - 1), block_indent, emptyafter=count_empty, indented=indented)
    
    # now after while loop exit we reached the end of document
    return Block((start_line, start_line + i - count_empty - 1), block_indent, emptyafter=count_empty, indented=indented)

if __name__ == '__main__':
    pass