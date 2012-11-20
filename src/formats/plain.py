import core.fileparser
from core.args import args
from core.blockparser import block_is_centered, block_is_header

def reformat(block, margin=None):
    from gntools.texts.typesetting import centerize, reform_par

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

    spec = block_is_centered(block, margin=margin) or block_is_header(block)
    next_spec = block_is_centered(block.next, _try = True, margin=margin) or block_is_header(block.next, True)

    empties = '\n'*block.emptyafter*(spec or next_spec or args.i == 0)

    if block_is_centered(block, margin=margin):
        return centerize(block.raw_content().strip(), args.m) + empties

    if block_is_header(block):
        return block.raw_content() + empties

    if block_is_header(block.prev, True) and args.nofirstind:
        return reform_par(block.raw_content(), args.l, 0, args.j, args.m) + empties

    return reform_par(block.raw_content(), args.l, args.i, args.j, args.m) + empties

def _main(first_block):
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
