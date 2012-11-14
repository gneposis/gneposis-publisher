import core.fileparser
from core.args import args

def reformat(block, margin=None):
    from gntools.texts.typesetting import centerize, reform_par

    def block_is_centered(block, _try = False):
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
        if block:
            headers = core.fileparser.HEADERS
            if _try:
                try:
                    if block.type() in headers:
                        return True
                except:
                        return False
            if block.type() in headers:
                return True
        return False

    # check arguments

    if args.nohyph:
        hyph_lang = None
    else:
        hyph_lang = args.l

    if args.nojust:
        just = None
    else:
        just = args.j

    # check block environment speciality

    spec = block_is_centered(block) or block_is_header(block)
    next_spec = block_is_centered(block.next, True) or block_is_header(block.next, True)

    empties = '\n'*block.emptyafter*(spec or next_spec)

    if block_is_centered(block):
        return centerize(block.raw_content.strip(), args.m) + empties

    if block_is_header(block):
        return block.raw_content + empties

    if block_is_header(block.prev, True) and args.nofirstind:
        return reform_par(block.raw_content, hyph_lang, margin=args.m, indent=0, justify=just) + empties

    return reform_par(block.raw_content, hyph_lang, margin=args.m, indent=args.i, justify=just) + empties

def main(first_block):
    from gntools.filepath import backup, writeout
    
    b = first_block

    if not args.M:
        wm = core.fileparser.wrapmargin(first_block)
    else:
        wm = args.M

    if args.o:
        backup(args.o)

    while b.next:
        writeout(reformat(b, margin=wm) + '\n', args.o)
        b = b.next
    writeout(reformat(b, margin=wm) + '\n', args.o)
