import gntools.lines

import core.raw
import core.rules

class NonInlineStatementInline(ValueError): pass
class MetaStatementNotInPreamble(ValueError): pass
class InvalidRawIndex(ValueError): pass

def get_statements(raw = core.raw.make()):
    i = 0
    loop = True
    statements = []
    while loop:
        loc = core.raw.get_statement(raw, st=i)
        if loc:
            statements.append((loc, core.raw.statement_parser(raw[loc[0]:loc[1]])))
            i = loc[1]
        else:
            loop = False
    return tuple(statements)

def statement_wholelinecheck(raw = core.raw.make()):
    lns = gntools.lines.newlines(raw)
    stm = get_statements(raw)
    checklist = []
    for i in stm:
        try:
            j = lns.index(i[0][0])
            k = lns.index(i[0][1]+1)
            if j + 1 == k:
                checklist.append(True)
            else:
                checklist.append(False)
        except:
            checklist.append(False)
    return tuple(checklist)

def inline_check(raw = core.raw.make(), rls = core.rules.make()):
    stm = get_statements(raw)
    wln = statement_wholelinecheck(raw)
    l = []
    for i in range(len(wln)):
        if not wln[i] and not rls[stm[i][1][0]]['options'].get('inline', False):
            l.append(raw[stm[i][0][0]:stm[i][0][1]])
    if l:
        raise NonInlineStatementInline('The following statements must have their own line: {0}'.format(l))

def statement_metacheck(raw = core.raw.make(), rls = core.rules.make()):
    stm = get_statements(raw)
    checklist = []
    for i in stm:
        if rls[i[1][0]]['options'].get('meta', False):
            checklist.append(True)
        else:
            checklist.append(False)
    return tuple(checklist)

def meta_check(raw = core.raw.make(), rls = core.rules.make()):
    stm = get_statements(raw)
    met = statement_metacheck(raw, rls)
    l = []
    preamble = True
    for i in range(len(met)):
        if preamble and not met[i]:
            j = i
            preamble = False
        elif not preamble and met[i]:
            l.append(raw[stm[i][0][0]:stm[i][0][1]])
    if l:
        raise MetaStatementNotInPreamble('The following statements must be in the beginning of the document: {0}'.format(l))
    return j

def statement_filter(key = None, option = None, value = None, Indices = True, raw = core.raw.make(), rls = core.rules.make()):
    stm = get_statements(raw)
    result_key = []
    result_option = []
    for i in stm:
        if not key:
            result_key.append(True)
        elif key == i[1][0]:
            result_key.append(True)
        else:
            result_key.append(False)
        o = rls[i[1][0]]['options'].get(option, False)
        if not option:
            result_option.append(True)
        elif o and value and o == value:
            result_option.append(True)
        elif o and not value:
            result_option.append(True)
        else:
            result_option.append(False)
    result = [result_key[k] and result_option[k] for k in range(len(stm))]
    if Indices:
        indices_result = []
        for i in range(len(result)):
            if result[i]:
                indices_result.append(i)
        return tuple(indices_result)
    else:
        return tuple(result)

# HIBÁS: fordítva indexeli l_endable-t
def statement_ranges(raw = core.raw.make(), rls = core.rules.make()):
    stm = get_statements(raw)
    l_endable = list(statement_filter(option='endable'))
    def endable_ends():
        l_end = list(statement_filter(option='end', Indices = False))
        l_endall = statement_filter(option='endall', Indices = False)
        l_endable.reverse()
        ee_result = []
        for i in l_endable:
            for j in range(len(stm) - i):
                if l_end[-j] or l_endall[-j]:
                    k = j
            if l_end[-k]:
                l_end[-k] = False
            ee_result.insert(0, len(stm) - k)
        return ee_result
    result = []
    for i in range(len(stm)):
        if i in l_endable:
            result.append((stm[i][0][0], stm[endable_ends()[l_endable.index(i)]][0][1]))
        else:
            result.append(stm[i][0])
    return result

def get_statement_index(i, key = None, option = None, value = None, raw = core.raw.make(), rls = core.rules.make()):
    stm = get_statements(raw)
    if not (0<=i<=len(raw)):
        raise InvalidRawIndex('Index is out of range of the raw document. It must be non-negative and in this case it must be less than or equal to {0}.'.format(len(raw)))
    l_stm = statement_filter(key, option, value, raw, rls)
    for j in range(len(l_stm)):
        if l_stm[j]:
            s = stm[j][0][0]
            if j == len(stm) -1:
                e = len(raw)
            else:
                e = stm[j+1][0][0] -1
            if (s<=i<=e):
                return j

def class_lines(raw = core.raw.make(), rls = core.rules.make()):
    lns = gntools.lines.newlines(raw)
    