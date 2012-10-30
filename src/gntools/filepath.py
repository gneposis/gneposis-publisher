import os
import sys

class FileNotFoundError(IOError): pass

class File:
    def __init__(self, f, string=False):
        if not f:
            raise FileNotFoundError

        if string:
            ff = f
        else:
            ff = f.name
        
        self.path = os.path.split(ff)[0]
        self.fext = os.path.split(ff)[1]

        if len(self.fext.split('.')) > 1:
            self.f = '.'.join(self.fext.split('.')[0:-1])
            self.ext = self.fext.split('.')[-1]
        else:
            self.f = self.fext
            self.ext = ''

prog_path = os.path.abspath('')

def ensure_dir(f):
    # Code is from: http://stackoverflow.com/questions/273192/python-best-way-to-create-directory-if-it-doesnt-exist-for-file-write
    '''Creates directory for output file if not exits.'''
    if not os.path.exists(f):
        os.makedirs(f)
    return f
