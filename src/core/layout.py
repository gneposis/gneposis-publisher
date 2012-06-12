import core.raw

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