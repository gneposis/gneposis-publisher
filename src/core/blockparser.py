from core.meta import base_constants

def author(first_block):
    '''Returns the name of the author'''
    b = first_block
    while b.next:
        if b.type() == 'author':
            find_by = b.raw_content().lower().find(base_constants['by'])
            if find_by == 0:
                return b.raw_content()[len(base_constants['by']):].strip()
            return b.raw_content().strip()
        b = b.next

def title(first_block):
    '''Returns the title'''
    b = first_block
    while b.next:
        if b.type() == 'title':
            return b.raw_content().strip()
        b = b.next

def nr(block):
    '''Returns the number of the block'''
    n = 0
    b = block
    try:
        while b.llink:
            n += 1
            b = b.llink
    except:
        return n
    return n

def block_is_centered(block, _try = False, margin=None):
    if block:
        if _try:
            try:
                if margin in block.centered_at() and block.leftmargin():
                    return True
            except:
                    return False
        if margin in block.centered_at() and block.leftmargin():
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
