import pickle

from .opts import filefile, filepath
from gntools import md5 

def save(hashdata, data):
    pickledata = (md5.data(hashdata),data)
    with open(filepath+'/'+filefile+'.gp', 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(pickledata, f, pickle.HIGHEST_PROTOCOL)

def load(data):
    try:
        with open(filepath+'/'+filefile+'.gp', 'rb') as f:
            # The protocol version used is detected automatically, so we do not
            # have to specify it.
            pickledata = pickle.load(f)
            if pickledata[0] == md5.data(data):
                return pickledata[1]
    except:
        return None