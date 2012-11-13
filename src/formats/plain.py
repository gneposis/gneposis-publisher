import sys
import core.fileparser
from core.args import args,infile

from gntools.texts.typesetting import *
from gntools.filepath import backup, writeout
from gntools.lines import content

def reformat(block, margin=None):
    if args.nohyph:
        hyph_lang = None
    else:
        hyph_lang = args.l

    if args.nojust:
        just = None
    else:
        just = args.j

    headers = core.fileparser.HEADERS
    headers.append('centered')

    try:
        pt = block.prev.type()
    except:
        pt = None

    t = block.type()

    try:
        nt = block.next.type()
    except:
        nt = None

    if margin in block.centered_at() and block.leftmargin():
        centered = True
    else:
        centered = False    

    if t in headers or nt in headers or args.i==0 or centered:
        empties = True
    else:
        empties = False

    if centered:
        return centerize(block.raw_content.strip(), args.m) + '\n'*b.emptyafter*empties

    if t in headers:
        return block.raw_content + '\n'*b.emptyafter*empties
    
    if pt in headers and args.nofirstind:
        return reform_par(block.raw_content, hyph_lang, margin=args.m, indent=0, justify=just) + '\n'*b.emptyafter*empties

    return reform_par(block.raw_content, hyph_lang, margin=args.m, indent=args.i, justify=just) + '\n'*b.emptyafter*empties

if args.stline==1 and args.enline==0:
    first_block = core.fileparser.ll_blocks(core.args.infile)
else:
    if args.enline==0:
        args.enline=len(core.args.infile.splitlines())

    first_block = core.fileparser.ll_blocks(content(core.args.infile, args.stline, args.enline))
    
wm = core.fileparser.wrapmargin(first_block)

b = first_block

if args.o:
    backup(args.o)

while b.next:
    writeout(reformat(b, margin=wm) + '\n', args.o)
    b = b.next
writeout(reformat(b, margin=wm) + '\n', args.o)
