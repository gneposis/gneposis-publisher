import gpcmd
import gpconverter
import gnparser
import opts

with open(opts.path + '/data/declarations', encoding='utf-8') as a_file:
    rules = gpcmd.decrules(a_file.read())

with open(opts.file, encoding='utf-8') as a_file:
    raw = gpconverter.raw(a_file.read())
    
dictionary = gpcmd.declarations(raw, opts.path + '/data/languages/declarations/*')