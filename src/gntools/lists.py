class UncomparableObjects(ValueError): pass

def intersection_of_two_lists(reference, current):
    '''Intersects two lists.
    For example [0,5,7] and [2,5,None] returns [None, 5, None].
    However ['a', 8] and ['b', 0] returns None'''

    if not reference:
        return current
    elif not current:
        return None
    elif len(reference) != len(current):
        raise UncomparableObjects('The length of the two argument is different thus uncomparable!')
    
    isect = [None for i in range(len(reference))]
    r = range(len(reference))

    for i in r:
        if reference[i] == current[i]:
            isect[i] = reference[i]

    allnone = True
    # check if all None
    for i in r:
        if isect[i] != None:
            allnone = False
    
    if allnone:
        return None

    return isect

# code by Graddy: http://stackoverflow.com/a/8337168
def nth(n, _list, lookfor=True):
    '''Finds the nth True in a given list.'''
    c = 0
    for index,i in enumerate(_list):
        if i == lookfor:
            c += 1
            if c == n:
                return index
