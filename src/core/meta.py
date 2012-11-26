from gntools.filepath import datfile2dic, prog_path

from core.args import args
#from core.blockparser import first_block

LANG_PATH = '/data/languages'

def get_base_constants():
    datfile = prog_path + LANG_PATH + '/' +  args.l
    return datfile2dic(datfile)

base_constants = get_base_constants()

def get_uid():
    '''UID is practically the md5 hash of the input file'''
    from gntools.md5 import md5_of_file
    return md5_of_file(args.f)



#def author():
#    '''Returns the name of the author'''
#    b = first_block
#    while b.next:
#        if b.type() == 'author':
#            find_by = b.raw_content().lower().find(base_constants['by'])
#            if find_by == 0:
#                return b.raw_content()[len(base_constants['by']):].strip()
#            return b.raw_content().strip()
#        b = b.next
#
#def title():
#    '''Returns the title'''
#    b = first_block
#    while b.next:
#        if b.type() == 'title':
#            return b.raw_content().strip()
#        b = b.next

def date(): # I will write it soon
    return None

def description(): # I will write it soon
    return None

def isbn(): # I will write it soon
    return None

def sort_author(): # I will write it soon
    return None
