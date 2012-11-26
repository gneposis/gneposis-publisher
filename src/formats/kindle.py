from gntools.filepath import prog_path, load_path

from core.meta import base_constants
import core.blocks

STYLES_PATH = '/data/kindle'
HEADER = 'html_header'
NCX_HEADER = 'ncx_header'
OPF_HEADER = 'opf_header'

BODY_FILE = 'body.html'
COVER_FILE = 'cover.jpg'
CSS_FILE = 'css.css'
OPF_FILE = 'book.opf'
TITLEPAGE_FILE = 'titlepage.html'
TOC_NCX_FILE = 'toc.ncx'
TOCPAGE_FILE = 'tocpage.html'


def author(docheader):
    return docheader.frontmatter.titlepage.dlink.raw_content()

def title(docheader):
    return docheader.frontmatter.titlepage.dlink.rlink.raw_content()

def reformat_content(block):
    from gntools.texts.findrep import rep_env
    return rep_env(block.raw_content(),'_','_','<i>','</i>')

def reformat(block):
    if isinstance(block, core.blocks.Paragraph):
        if isinstance(block.prev, core.blocks.Heading):
            return '<p style="text-indent: 0em;">' + reformat_content(block) +'</p>' + '\n'
        return '<p>' + reformat_content(block) +'</p>' + '\n'
    elif isinstance(block, core.blocks.Break):
        return '<p class="asterism">***</p>' + '\n'
    elif isinstance(block, core.blocks.Heading):
        return '<div style="page-break-after:always"></div>'+'\n'+'<a name="'+block.nr()+'" href="'+TOCPAGE_FILE+'#'+block.nr()+'"><div class="chapter">'+reformat_content(block)+'</div></a>' + '\n'
    else:
        return ''

def html_header(docheader, style='default'):
    with open(prog_path+STYLES_PATH+'/'+style+'/'+HEADER, mode='r') as html_header_file:
        html_header = html_header_file.read()
    html_header = html_header.replace('AUTHOR: TITLE', author(docheader)+': '+title(docheader))
    return html_header

def html_footer():
    return '</body>\n</html>'

def body(docheader, style='default'):
    content = html_header(docheader, style)
    b = docheader
    while b.next:
        content += reformat(b)
        b = b.next
    content += reformat(b)
    return content + html_footer()

def css(style='default'):
    with open(prog_path+STYLES_PATH+'/'+style+'/'+CSS_FILE, mode='r') as css_file:
        content = css_file.read()
    return content

def opf(docheader, style='default'):
    from core.args import args
    from core.meta import get_uid, date, description, isbn, sort_author
    with open(prog_path+STYLES_PATH+'/'+style+'/'+OPF_HEADER, mode='r') as opf_header_file:
        content = opf_header_file.read()
    content = content.replace('UID', get_uid())
    content += '<dc:Title>'+title(docheader)+'</dc:Title>\n'
    content += '<dc:Language>'+args.l+'</dc:Language>\n'
    content += '<dc:Creator '
    if sort_author():
        content += 'opf:file-as="'+sort_author()+'" '
    content += 'opf:role="aut">'+author(docheader)+'</dc:Creator>\n'
    if date():
        content += '<dc:Date>'+date()+'</dc:Date>\n'
    if description():
        content += '<dc:Description>'+description()+'</dc:Description>\n'
    content += '<dc:Identifier id="uid">'+get_uid()+'</dc:Identifier>\n'
    if isbn():
        content += '<dc:Identifier opf:scheme="ISBN">'+isbn()+'</dc:Identifier>\n'
    content += '</dc-metadata>\n'
    content += '<x-metadata>\n'
    content += '<EmbeddedCover>'+COVER_FILE+'</EmbeddedCover>\n'
    content += '<output encoding="utf-8"></output>\n'
    content += '</x-metadata>\n'
    content += '<meta name="cover" content="my-cover-image" />\n'
    content += '</metadata>\n'
    content += '<manifest>\n'
    content += '<item id="my-cover-image" media-type="image/jpeg" href="'+COVER_FILE+'"/>\n'
    content += '<item id="titlepage" media-type="text/x-oeb1-document" href="'+TITLEPAGE_FILE+'"/>\n'
    content += '<item id="toc" media-type="application/x-dtbncx+xml" href="'+TOC_NCX_FILE+'"/>\n'
    content += '<item id="tocpage" media-type="text/x-oeb1-document" href="'+TOCPAGE_FILE+'"/>\n'
    content += '<item id="body" media-type="text/x-oeb1-document" href="'+BODY_FILE+'"/>\n'
    content += '</manifest>\n'
    content += '<spine toc="toc">\n'
    content += '<itemref idref="titlepage"/>\n'
    content += '<itemref idref="tocpage"/>\n'
    content += '<itemref idref="body"/>\n'
    content += '</spine>\n'
    content += '<guide>\n'
    content += '<reference type="text" title="Go to Beginning" href="'+TITLEPAGE_FILE+'"/>\n'
    content += '<reference type="toc" title="Table of Contents" href="'+TOCPAGE_FILE+'"/>\n'
    content += '</guide>\n'
    content += '</package>'
    return content

def titlepage(docheader, style='default'):
    content = html_header(docheader, style)
    content += '<a name="start"/>\n'
    content += '<div class="author">'+author(docheader)+'</div>\n'
    content += '<div class="title">'+title(docheader)+'</div>\n'
    return content + html_footer()

def toc_ncx(docheader, style='default'):
    from core.meta import get_uid
    with open(prog_path+STYLES_PATH+'/'+style+'/'+NCX_HEADER, mode='r') as ncx_header_file:
        content = ncx_header_file.read()
    content = content.replace('UID', get_uid())
    content += '<docTitle><text>'+title(docheader)+'</text></docTitle>\n'
    content += '<docAuthor><text>'+author(docheader)+'</text></docAuthor>\n'
    content += '<navMap>\n'
    block=docheader.mainmatter.dlink
    while block.rlink:
        content += '<navPoint class="chapter" id="'+block.nr()+'" playOrder="'+block.nr()+'"><navLabel><text>'+reformat_content(block)+'</text></navLabel><content src='+BODY_FILE+'#'+block.nr()+' /></navPoint>\n'
        block = block.rlink
    content += '<navPoint class="chapter" id="'+block.nr()+'" playOrder="'+block.nr()+'"><navLabel><text>'+reformat_content(block)+'</text></navLabel><content src='+BODY_FILE+'#'+block.nr()+' /></navPoint>\n'
    return content + '</navMap>\n</ncx>'

def tocpage(docheader, style='default'):
    content = html_header(docheader, style)
    content += '<div style="page-break-after:always"></div>'+'\n'
    content += '<a name="toc"><div class="chapter">'+base_constants['toctitle']+'</div></a>\n'
    block=docheader.mainmatter.dlink
    while block.rlink:
        content += '<a name="'+block.nr()+'" href="'+BODY_FILE+'#'+block.nr()+'"><div class="toc1">'+reformat_content(block)+'</div></a>\n'
        block = block.rlink
    content += '<a name="'+block.nr()+'" href="'+BODY_FILE+'#'+block.nr()+'"><div class="toc1">'+reformat_content(block)+'</div></a>\n'
    return content + html_footer()

def _main(docheader):
    print('\nGenerating files for kindlegen:', end='\n\n')

    print('Generating {0} ... '.format(BODY_FILE), end='')
    with open(load_path+'/'+BODY_FILE, mode='w', encoding='utf-8') as body_file:
        body_file.write(body(docheader))
    print('done.')

    print('Generating {0} ... '.format(CSS_FILE), end='')
    with open(load_path+'/'+CSS_FILE, mode='w', encoding='utf-8') as css_file:
        css_file.write(css())
    print('done.')

    print('Generating {0} ... '.format(OPF_FILE), end='')
    with open(load_path+'/'+OPF_FILE, mode='w', encoding='utf-8') as opf_file:
        opf_file.write(opf(docheader))
    print('done.')

    print('Generating {0} ... '.format(TITLEPAGE_FILE), end='')
    with open(load_path+'/'+TITLEPAGE_FILE, mode='w', encoding='utf-8') as titlepage_file:
        titlepage_file.write(titlepage(docheader))
    print('done.')

    print('Generating {0} ... '.format(TOC_NCX_FILE), end='')
    with open(load_path+'/'+TOC_NCX_FILE, mode='w', encoding='utf-8') as ncx_file:
        ncx_file.write(toc_ncx(docheader))
    print('done.')

    print('Generating {0} ... '.format(TOCPAGE_FILE), end='')
    with open(load_path+'/'+TOCPAGE_FILE, mode='w', encoding='utf-8') as toc_file:
        toc_file.write(tocpage(docheader))
    print('done.')