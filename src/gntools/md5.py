from functools import partial
from hashlib import md5

def file(fi):
    '''Returns the md5sum of a given file'''
    # Code is from http://stackoverflow.com/a/7829658
    with open(fi, mode='rb') as f:
        d = md5()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
    return d.hexdigest()

def data(data):
    '''Returns the md5sum of a given data'''
    d = md5()
    d.update(data.encode('utf-8'))
    return d.hexdigest()