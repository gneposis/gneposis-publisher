HEADERS = ['chapter']
HUGE_VALUE = 10000

class NonSupportedBlockError(ValueError): pass

class Block:
    # loc: tuple of start and end line number (st, en)
    # loc = (-1,0) is for the first block containing the empty lines at
    #     the beginning of the document in its self.emptyafter
    def __init__(self, l_lines, emptyafter=0):
        self.l_lines = l_lines
        self.emptyafter = emptyafter

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

    def centered(self, margin=None):
        '''Returns True if margin was given and if l_lines is centered.
        If no margin was given, returns the set of rightmargin(s) at which the content is centered.'''

        # At first it calculates the rightmargin value where the Block would be centered.
        # example "...b" gives {7}
        #         "...bl" gives {7,8}
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

        if margin in c_i and self.leftmargin():
            return True
        elif margin:
            return False
        else:
            return c_i

    def loc(self):
        l_n = []
        c = 0
        curr_pos = self
        while curr_pos.llink or curr_pos.ulink:
            c += 1
            if curr_pos.llink and not curr_pos.ulink:
                curr_pos = curr_pos.llink
            elif curr_pos.ulink and not curr_pos.llink:
                l_n.insert(0, c)
                c = 0
                curr_pos = curr_pos.ulink
            else:
                raise BothLeftAndUpLinkExistsError('ulink and rlink are mutually exclusive ATM!')
        return l_n

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
    def nr(self):
        loc = [str(i) for i in self.loc()]
        return '.'.join(loc)

class Author(Heading):
    pass

class Chapter(Heading):
    pass

class Title(Heading):
    pass

class SubTitle(Title):
    pass

class Paragraph(Block):
    def __init__(self, l_lines, emptyafter=0, indent=0):
        Block.__init__(self, l_lines, emptyafter)
        self.indent = len(self.l_lines[0]) - len(self.l_lines[0].lstrip())

    def nr(self):
        loc = [str(i) for i in self.loc()]
        return '.'.join(loc[:-1])+':'+loc[-1]

class Break(Block):
    def __init__(self, l_lines, emptyafter=0):
        Block.__init__(self, l_lines, emptyafter)
