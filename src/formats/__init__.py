from core.args import args

if args.mode == 'plain':
    from formats.plain import _main
elif args.mode == 'kindle':
    from formats.kindle import _main

def main(firstblock):
    return _main(firstblock)