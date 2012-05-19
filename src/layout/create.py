import re
from .declarat import parser
from core.pickler import load, save
from gntools.lines import content, newlines, nr

def layout(data, rules, dictionary, debug=False, pr=False):
    '''Creates a raw dictionary of all the declarations.
    
    usage:
    layout[line]
    , where line is the line of declaration in the data.
    
    For example:
    layout[1]
    returns
    {'nextsamedeclaration': None, 'nextdeclaration': 2, 'name': 'Jane Austen',
        'key': 'author', 'sortname': 'Austen, Jane'}
    
    key shows the declaration key
    nextdeclaration shows the line of the next declaration.
    nextsamedeclaration shows the line of the next identical declaration
    if any.
    remaining keys are determined by rules
    '''
    # Since analization is a long process you want to import a saved layout if
    # possible, and data is identical to the one the save based on. 'load'
    # function will do that. You want to force analyzation if debug is True.
    if not debug and load(data):
        if pr == True:
            print('\rGenerating layout using saved layout file...'.ljust(61),end='')
        layout = load(data)
    else:
    # Now you want to define a list for your struct elements.
        layout = []
        _newlines = newlines(data)
        find_loc = 0
        line = 1
        st = 0
        while find_loc>=0:
            find_loc = data[st:].find('{')
            if find_loc>=0:
                previousline = line
                line = nr(find_loc + st, data)
                st = _newlines[line]
                # Since it can be a long process, you want to put a progress
                # message.
                if pr == True:
                    print('\rGenerating layout: {0}/{1} ({2}%)'.format(line,len(_newlines),round(line/len(_newlines)*100,1)).ljust(61),end='')
                # You want to get the content of the current line
                c = content(line, data)
                # Now you want to search for anything between {}-s.
                p = re.compile(r'{.+?}')
                # Since there can be more match, you want them all. 'fi' will
                # return the list of them and you will get the column from it
                fi, it = p.findall(c), p.finditer(c)
                if fi:
                    i = 0
                    for e in it:
                        # Add the data parser can get, first.
                        layout.append(parser(fi[i], rules, dictionary))
                        # Now the current line number in data.
                        layout[-1].update(line=line)
                        # Now the start and end column of the match.
                        layout[-1].update(column=e.span())
                        # Now you want to add css names based on key. However,
                        # you want to know if a section comes immediately after
                        # a chapter, so you can handle the vertical spaces
                        # between those titles in the css file of your html.
                        _key = parser(fi[i], rules, dictionary)['key']
                        try:
                            _previouskey = layout[-2]['key']
                        except:
                            _previouskey = None            
                        if previousline + 1 == line and _previouskey and rules[_previouskey]['options'].get('level',None) and rules[_key]['options'].get('level',None):
                            # If key follows previouskey immediately, you want
                            # css name to be the concatenation of the two.
                            layout[-1].update(css=_key+_previouskey)
                        # Now you want to include the nr of key:
                        c = 0
                        k = -1
                        loop = True
                        while loop:
                            try:
                                if layout[k]['key'] == _key:
                                    c += 1
                                    k -= 1
                                else:
                                    k -= 1
                            except:
                                loop = False
                        layout[-1].update(nr=c)
                        
                        i += 1
                        
            else:
                if pr == True:
                    print('\rGenerating layout: {0}/{0} (100%)'.format(len(_newlines)).ljust(61),end='')
        
        # You want to save the layout since it is a long process to get.
        # Moreover, future calls will be fast as hell...
        save(data, layout)
    if pr == True:
        print('[DONE]'.rjust(7))
    return tuple(layout)
