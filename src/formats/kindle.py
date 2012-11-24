from gntools.filepath import prog_path, load_path

from core.fileparser import tree_struct
from core.blockparser import author, title, nr, block_is_header
from core.meta import base_constants

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

def reformat_content(block):
    from gntools.texts.findrep import rep_env
    return rep_env(block.raw_content(),'_','_','<i>','</i>')

def reformat(block):
    if block.type() == 'paragraph':
        if block_is_header(block.prev):
            return '<p style="text-indent: 0em;">' + reformat_content(block) +'</p>' + '\n'
        return '<p>' + reformat_content(block) +'</p>' + '\n'
    elif block.type() == 'asterism':
        return '<p class="asterism">***</p>' + '\n'
    elif block.type() == 'chapter':
        return '<div style="page-break-after:always"></div>'+'\n'+'<a name="'+str(nr(block))+'" href="'+TOCPAGE_FILE+'#'+str(nr(block))+'"><div class="chapter">'+reformat_content(block)+'</div></a>' + '\n'
    else:
        return ''

def html_header(first_block, style='default'):
    with open(prog_path+STYLES_PATH+'/'+style+'/'+HEADER, mode='r') as html_header_file:
        html_header = html_header_file.read()
    html_header = html_header.replace('AUTHOR: TITLE', author(first_block)+': '+title(first_block))
    return html_header

def html_footer():
    return '</body>\n</html>'

def body(first_block, style='default'):
    tree_struct(first_block)
    content = html_header(first_block, style)
    b = first_block
    while b.next:
        content += reformat(b)
        b = b.next
    content += reformat(b)
    return content + html_footer()

def css(style='default'):
    with open(prog_path+STYLES_PATH+'/'+style+'/'+CSS_FILE, mode='r') as css_file:
        content = css_file.read()
    return content

def opf(first_block, style='default'):
    from core.args import args
    from core.meta import get_uid, date, description, isbn, sort_author
    with open(prog_path+STYLES_PATH+'/'+style+'/'+OPF_HEADER, mode='r') as opf_header_file:
        content = opf_header_file.read()
    content = content.replace('UID', get_uid())
    content += '<dc:Title>'+title(first_block)+'</dc:Title>\n'
    content += '<dc:Language>'+args.l+'</dc:Language>\n'
    content += '<dc:Creator '
    if sort_author():
        content += 'opf:file-as="'+sort_author()+'" '
    content += 'opf:role="aut">'+author(first_block)+'</dc:Creator>\n'
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

def titlepage(first_block, style='default'):
    content = html_header(first_block, style)
    content += '<a name="start"/>\n'
    content += '<div class="author">'+author(first_block)+'</div>\n'
    content += '<div class="title">'+title(first_block)+'</div>\n'
    return content + html_footer()

def toc_ncx(first_block, style='default'):
    from core.meta import get_uid
    with open(prog_path+STYLES_PATH+'/'+style+'/'+NCX_HEADER, mode='r') as ncx_header_file:
        content = ncx_header_file.read()
    content = content.replace('UID', get_uid())
    content += '<docTitle><text>'+title(first_block)+'</text></docTitle>\n'
    content += '<docAuthor><text>'+author(first_block)+'</text></docAuthor>\n'
    content += '<navMap>\n'
    block=first_block.dlink
    while block.rlink:
        content += '<navPoint class="chapter" id="'+str(nr(block))+'" playOrder="'+str(nr(block))+'"><navLabel><text>'+reformat_content(block)+'</text></navLabel><content src='+BODY_FILE+'#'+str(nr(block))+' /></navPoint>\n'
        block = block.rlink
    content += '<navPoint class="chapter" id="'+str(nr(block))+'" playOrder="'+str(nr(block))+'"><navLabel><text>'+reformat_content(block)+'</text></navLabel><content src='+BODY_FILE+'#'+str(nr(block))+' /></navPoint>\n'
    return content + '</navMap>\n</ncx>'

def tocpage(first_block, style='default'):
    content = html_header(first_block, style)
    content += '<div style="page-break-after:always"></div>'+'\n'
    content += '<a name="toc"><div class="chapter">'+base_constants['toctitle']+'</div></a>\n'
    block=first_block.dlink
    while block.rlink:
        content += '<a name="'+str(nr(block))+'" href="'+BODY_FILE+'#'+str(nr(block))+'"><div class="toc1">'+reformat_content(block)+'</div></a>\n'
        block = block.rlink
    content += '<a name="'+str(nr(block))+'" href="'+BODY_FILE+'#'+str(nr(block))+'"><div class="toc1">'+reformat_content(block)+'</div></a>\n'
    return content + html_footer()

def _main(first_block):
    with open(load_path+'/'+BODY_FILE, mode='w', encoding='utf-8') as body_file:
        body_file.write(body(first_block))

    with open(load_path+'/'+CSS_FILE, mode='w', encoding='utf-8') as css_file:
        css_file.write(css())

    with open(load_path+'/'+OPF_FILE, mode='w', encoding='utf-8') as opf_file:
        opf_file.write(opf(first_block))

    with open(load_path+'/'+TITLEPAGE_FILE, mode='w', encoding='utf-8') as titlepage_file:
        titlepage_file.write(titlepage(first_block))

    with open(load_path+'/'+TOC_NCX_FILE, mode='w', encoding='utf-8') as ncx_file:
        ncx_file.write(toc_ncx(first_block))

    with open(load_path+'/'+TOCPAGE_FILE, mode='w', encoding='utf-8') as toc_file:
        toc_file.write(tocpage(first_block))