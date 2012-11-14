import argparse

FORMAT_PLAINTEXT_NAME = 'plain'
FORMAT_KINDLEMOBI_NAME = 'kindle'

# top-level parser
parser = argparse.ArgumentParser(description='Converts plain text to various formats.')

parser.add_argument('-v', action='version', version='0.01')
subparsers = parser.add_subparsers(title='output formats', description='valid formats', help='Supported output formats')
                                  
# create the parser for the FORMAT_PLAINTEXT_NAME command
plaintext = subparsers.add_parser(FORMAT_PLAINTEXT_NAME, help='Typesets a plain text file.')
plaintext.add_argument('-i', type=int, default=2, metavar='2', help='Value of indentification of paragraphs')
plaintext.add_argument('-j', default='deep', metavar='deep', help='Method of justification of paragraphs')
plaintext.add_argument('-l', default='en_GB', metavar='en_GB', help='Sets the language of document (default: none)')
plaintext.add_argument('-m', type=int, default=66, metavar='66', help='Sets the margin of the output document (default: 66)')
plaintext.add_argument('-M', type=int, default=0, metavar='72', help='Sets the margin of the input document (autodetect by default)')
plaintext.add_argument('-o',  help='output file', metavar='outfile')    
plaintext.add_argument('-nohyph', action='store_true', help='Turns of hyphenation')
plaintext.add_argument('-nofirstind', action='store_true', help='Makes the first line after heading not indented')
plaintext.add_argument('-nojust', action='store_true', help='Turns of justification')
plaintext.add_argument('f',  help='input file', metavar='infile')

plaintext.add_argument('--debug', action='store_true', help=argparse.SUPPRESS)
plaintext.add_argument('--mode', default=FORMAT_PLAINTEXT_NAME, help=argparse.SUPPRESS)
plaintext.add_argument('--stline', type=int, default=1, help=argparse.SUPPRESS)
plaintext.add_argument('--enline', type=int, default=0, help=argparse.SUPPRESS)

# create the parser for the FORMAT_KINDLEMOBI_NAME command
kindlemobi = subparsers.add_parser(FORMAT_KINDLEMOBI_NAME, help='Converts a plain text file to Kindle MOBI format.')
kindlemobi.add_argument('--baz', choices='XYZ', help='baz help')
kindlemobi.add_argument('--mode', default=FORMAT_KINDLEMOBI_NAME, help=argparse.SUPPRESS)
kindlemobi.add_argument('f',  help='input file', metavar='file')

args = parser.parse_args()         

with open(args.f, mode="r", encoding="utf-8") as a_file:
    infile = a_file.read()

if args.enline == 0:
    args.enline = len(infile.splitlines())
