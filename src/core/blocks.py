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

class Break(Block):
    def __init__(self, l_lines, emptyafter=0):
        Block.__init__(self, l_lines, emptyafter)
