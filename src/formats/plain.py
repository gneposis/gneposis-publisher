import core.fileparser
from core.args import args
import core.blocks

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

    spec = block.centered(margin=margin) or isinstance(block, core.blocks.Heading)
    if block.next:
        next_spec = block.next.centered(margin=margin) or isinstance(block.next, core.blocks.Heading)
    else:
        next_spec = False

    empties = '\n'*block.emptyafter*(spec or next_spec or args.i == 0)

    if block.centered(margin=margin):
        return centerize(block.raw_content().strip(), args.m) + empties

    if isinstance(block, core.blocks.Heading):
        return block.raw_content() + empties

    if isinstance(block.prev, core.blocks.Heading) and args.nofirstind:
        return reform_par(block.raw_content(), args.l, 0, args.j, args.m) + empties

    return reform_par(block.raw_content(), args.l, args.i, args.j, args.m) + empties

def _main(docheader):
    from gntools.filepath import backup, writeout

    def _writeout(b):
        nonlocal replace_lines

        def to_console(block, replace_lines):
            nonlocal nr
            log_string = 'Generating block: ' + nr + '\n\n'
            content = reformat(block, margin=args.M) + '\n'
            writeout(log_string + content, False, replace_lines=replace_lines)
            return log_string.count('\n') + content.count('\n')

        try:
            nr = b.nr()
        except:
            nr = ''

        if args.o:
            writeout('Generating block: ' + nr, False, replace_lines=1)
            writeout(reformat(b, margin=args.M) + '\n', args.o)
        else:
            replace_lines = to_console(b, replace_lines)


    print('\nGenerating output plain text:', end='\n\n')

    b = docheader

    if args.o:
        backup(args.o)

    replace_lines = 1
    while b.next:
        _writeout(b)
        b = b.next
    _writeout(b)

    if args.o:
        print(' ... done.')
