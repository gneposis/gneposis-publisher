import pickle

import opts
from gntools import md5

def save(hashdata, data):
    pickledata = (md5(hashdata),data)
    with open(opts.filepath+'/'+opts.filefile+'.gp', 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(pickledata, f, pickle.HIGHEST_PROTOCOL)

def load(data):
    try:
        with open(opts.filepath+'/'+opts.filefile+'.gp', 'rb') as f:
            # The protocol version used is detected automatically, so we do not
            # have to specify it.
            pickledata = pickle.load(f)
            if pickledata[0] == md5(data):
                return pickledata[1]
    except:
        return None