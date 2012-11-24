HEADERS = ['chapter']
HUGE_VALUE = 10000

class Block:
    # loc: tuple of start and end line number (st, en)
    # loc = (-1,0) is for the first block containing the empty lines at
    #     the beginning of the document in its self.emptyafter
    def __init__(self, l_lines):
        self.l_lines = l_lines

        self.emptyafter = 0

        self.prev = None
        self.next = None
        self.dlink = None
        self.ulink = None
        self.llink = None
        self.rlink = None

    def raw_content(self):
        c = ' '.join(self.l_lines)
        c = c.replace('\u2010 ','') # remove hyphens
        while c.find('  ') > -1:
            c = c.replace('  ',' ') # trim double spaces
        return c.strip()

class DocumentHeader(Block):

    class FrontMatter(Block):

        class TitlePage(Block):
            def __init__(self):
                Block.__init__(self,[''])

        def __init__(self):
            Block.__init__(self,[''])
            self.titlepage = self.TitlePage()


    class MainMatter(Block):
        def __init__(self):
            Block.__init__(self,[''])

    class BackMatter(Block):
        def __init__(self):
            Block.__init__(self,[''])

    def __init__(self, emptyafter):
        Block.__init__(self,[''])
        self.emptyafter = emptyafter
        self.frontmatter = self.FrontMatter()
        self.mainmatter = self.MainMatter()
        self.backmatter = self.BackMatter()

class Heading(Block):
    pass

class Chapter(Heading):
    pass

class Paragraph(Block):
    pass

class Separator(Block):
    pass

def get_block(l_lines, margin):

    def leftmargin():
        '''Returns the column number of the left margin'''
        m = HUGE_VALUE
        for i in l_lines:
            m = min(m,len(i) - len(i.lstrip()))
        return m

    def rightmargin():
        '''Returns the column number of the left margin'''
        m = 0
        for i in l_lines:
            m = max(m,len(i))
        return m

    def centered():
        '''Returns True if l_lines is centered.'''

        # At first it calculates the rightmargin value where the Block would be centered.
        # example "...b" gives {7}
        #         "...bl" gives {7,8}
        c_i = set()
        for i in l_lines:
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

        if margin in c_i and leftmargin():
            return True
        return False

    def block_is_header(block, _try = False):
        from core.fileparser import HEADERS
        if block:
            if _try:
                try:
                    if block.type() in HEADERS:
                        return True
                except:
                        return False
            if block.type() in HEADERS:
                return True
        return False

    def get_header(content):
        '''Returns header if header type in content'''
        for i in HEADERS:
            if block.raw_content().lower().find(base_constants[i]) > -1:
                return i
        return False

    if centered():
        if len(l_lines) == 1:
            content = l_lines[0]
            if content.lower().find('chapter') > -1:
                block = Chapter(l_lines)
            elif content == '***':
                block = Separator(l_lines)
            else:
                block = Heading(l_lines)
        else:
            block = Paragraph(l_lines)
    else:
        block = Paragraph(l_lines)

    return block
