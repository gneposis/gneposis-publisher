'''
Created on Apr 20, 2012

@author: adam
'''

import os
import sys
from optparse import OptionParser

def ensure_dir(f):
    # Code is from: http://stackoverflow.com/questions/273192/python-best-way-to-create-directory-if-it-doesnt-exist-for-file-write
    '''Creates directory for output file if not exits.'''
    if not os.path.exists(f):
        os.makedirs(f)
    return f

parser = OptionParser()
parser.add_option('-f', '--file', action='store', type='string', dest='filename')
(options, args) = parser.parse_args()

path = os.path.abspath(os.path.split(sys.argv[0])[0])

file = options.filename
filepath = os.path.split(file)[0]
filefull = os.path.split(file)[1]

if len(filefull.split('.')) > 1:
    filefile = '.'.join(filefull.split('.')[0:-1])
    fileext = filefull.split('.')[-1]
else:
    filefile = filefull
    fileext = None

decmainpath = path + '/data/declarations'
decpath = path + '/data/languages/declarations/*'
titpath = path + '/data/languages/titles/*'



#===============================================================================
# temporary
#===============================================================================
mode = 'kindle'