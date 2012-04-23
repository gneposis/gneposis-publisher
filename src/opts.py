'''
Created on Apr 20, 2012

@author: adam
'''

import os
import sys
from optparse import OptionParser

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

declarations = path + '/data/declarations'
decpath = path + '/data/languages/declarations/*'



#===============================================================================
# temporary
#===============================================================================
mode = 'kindle'