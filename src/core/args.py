import argparse

parser = argparse.ArgumentParser(description='Converts plain text to Kindle ebook format.')

parser.add_argument('f',  help='input file', metavar='file')
parser.add_argument('-v', action='version', version='0.01')

parsed = parser.parse_args()         

with open(parsed.f, mode="r", encoding="utf-8") as a_file:
    infile = a_file.read()  
