import pandas as pd


def is_non_terminal(word):  # all non-terminals are upper-case
    return word.isupper()


def is_terminal(word):  # all terminals are lower-case
    return not (word.isupper()) and not (word == '#')


def run(address):
    global grammar, non_terminal_tokens_Array, terminal_tokens_Array
    grammar = open(address, 'r').read().split('\n')  # read grammar lines
    for line in grammar:
        line = line.split(' ')  # read token
        non_terminal_tokens_Array.append(line[0])
        for j in range(len(line) - 2):
            word = line[j + 2]
            if is_terminal(word):
                terminal_tokens_Array.append(word)
    terminal_tokens_Array = list(set(terminal_tokens_Array))
    terminal_tokens_Array.sort()
    terminal_tokens_Array.append('$')
    non_terminal_tokens_Array = list(set(non_terminal_tokens_Array))
    non_terminal_tokens_Array.remove('S')
    non_terminal_tokens_Array.sort()
    non_terminal_tokens_Array = ['S'] + non_terminal_tokens_Array
    print_nonTerminal_and_terminals()
    print_isNullable()
    print_firsts()
    print_follows()
    print_parse_table()
    print_RHS_Table()


def print_parse_table():
    print("\n--------------------")
    print("|    Parse Table    |")
    print("--------------------\n")
    update_parse_table()


def print_RHS_Table():
    print("\n--------------------")
    print("|     RHS Table     |")
    print("--------------------\n")
    global grammar
    for i in range(len(grammar)):
        rhs = update_rhs(grammar[i])
        print(str(i) + ": ", end=' ')
        if rhs:
            for j in rhs:
                print(j, end=' ')
        print()
    print()
    return


def print_nonTerminal_and_terminals():
    print("\nTerminals & $: ", end="")
    print(terminal_tokens_Array)
    print("\nNon Terminals: ", end="")
    print(non_terminal_tokens_Array)


def is_nullable(non_terminal_token):
    global grammar
    is_null = False
    for line in grammar:
        line = line.split(' ')  # tokens in grammar line
        if non_terminal_token == line[0]:
            if line[2] != '#':
                for i in line[2:]:
                    if is_terminal(i) or (not (is_nullable(i))):
                        is_null = False
                        break
                    else:
                        is_null = True
            else:
                return True
        if is_null:
            break
    return is_null


def print_isNullable():
    print("\n--------------------")
    print("|    isNullable    |")
    print("--------------------\n")
    for non_terminal_token in non_terminal_tokens_Array:
        nullable_token = is_nullable(non_terminal_token)
        if nullable_token:
            print("\" " + non_terminal_token + " \" " + "is nullable ")
        else:
            print("\" " + non_terminal_token + " \" " + "is not nullable ")


def exe_first_set(non_terminal_token):
    global grammar
    first_array = []
    for line in grammar:
        line = line.split(' ')  # tokens in grammar line
        line_len = len(line)  # size of a line in grammar
        if non_terminal_token == line[0]:  # rows that are started with this non terminal
            if is_non_terminal(line[2]):
                first_line2 = exe_first_set(line[2])
                if first_line2:
                    first_array = first_array + first_line2
                for i in range(line_len - 2):
                    if is_nullable(line[i + 2]):
                        next_index = i + 3
                        if next_index < line_len:
                            if is_non_terminal(line[next_index]):
                                first_line_next_index = exe_first_set(line[next_index])
                                if first_line_next_index:
                                    first_array = first_array + first_line_next_index
                            else:
                                first_array.append(line[next_index])
                                break
                        else:
                            break
                    else:
                        break
            elif is_terminal(line[2]):
                first_array.append(line[2])

    return list(set(first_array))


def print_firsts():
    print("\n--------------------")
    print("|       First       |")
    print("--------------------\n")
    for non_terminal in non_terminal_tokens_Array:
        first = exe_first_set(non_terminal)
        if first:
            print(non_terminal + ": " + first[0], end="")
            for i in range(len(first) - 1):
                print("," + first[i + 1], end="")
            print()
        else:
            print(non_terminal + ": []")


def exe_follow_relative_set(prev_token, next_token):  # if follow was a non-terminal
    global grammar
    relative = grammar[:]
    for line in grammar:
        i = line.split()
        if i[0] == next_token:
            for j in i[2:]:
                if j == prev_token:
                    grammar.remove(line)
    follow = exe_follow_set(prev_token)
    grammar = relative[:]
    return follow


def exe_follow_set(non_terminal):
    global grammar
    follow_array = []
    if non_terminal == 'S':
        follow_array.append('$')
    for line in grammar:
        line = line.split(' ')
        line_len = len(line)
        for i in range(line_len - 2):
            if line[i + 2] == non_terminal:
                for j in range(line_len - 2 - i):
                    next_index = i + j + 3
                    if next_index >= line_len:
                        if (line[0] not in get_follow_rel(line[i + j + 2])) or (line[i + j + 2] not in get_follow_rel(line[0])):
                            follow_prev_token = exe_follow_set(line[0])
                            if follow_prev_token:
                                follow_array = follow_array + follow_prev_token
                        else:
                            if line[0] != line[i + j + 2]:
                                follow_relative = exe_follow_relative_set(line[0], line[i + j + 2])
                                if follow_relative:
                                    follow_array = follow_array + follow_relative
                    else:
                        if not is_terminal(line[next_index]):
                            first = exe_first_set(line[next_index])
                            if first:
                                follow_array = follow_array + first
                            if not (is_nullable(line[next_index])):
                                break
                        else:
                            follow_array.append(line[next_index])
                            break
    return list(set(follow_array))


def get_follow_rel(non_terminal):
    global grammar
    relative = []
    for row in grammar:
        row = row.split(' ')
        row_len = len(row)
        for i in range(row_len - 2):
            if non_terminal == row[i + 2]:
                if is_non_terminal(row[row_len-1]):
                    relative.append(row[0])

    return list(set(relative))




def print_follows():
    print("\n--------------------")
    print("|      Follow      |")
    print("--------------------\n")
    for non_terminal in non_terminal_tokens_Array:
        follow = exe_follow_set(non_terminal)
        if follow:
            print(non_terminal + ": " + follow[0], end="")
            for i in range(len(follow) - 1):
                print("," + follow[i + 1], end="")
            print()
        else:
            print(non_terminal + ": []")


def update_parse_table():
    global grammar
    dataframe = pd.DataFrame(index=non_terminal_tokens_Array, columns=terminal_tokens_Array)
    for i in range(len(grammar)):
        line = grammar[i].split(' ')
        line_len = len(line)
        if line[2] == '#':
            follow = exe_follow_set(line[0])
            if follow:
                for j in follow:
                    dataframe.loc[[line[0]], [j]] = "[" + str(i) + "]"
        else:
            if is_terminal(line[2]):
                dataframe.loc[[line[0]], [line[2]]] = "[" + str(i) + "]"
            else:
                first = exe_first_set(line[2])
                if first:
                    for j in first:
                        dataframe.loc[[line[0]], [j]] = "[" + str(i) + "]"
                for k in range(line_len - 2):
                    if is_nullable(line[k + 2]):
                        next_index = k + 3
                        if next_index < line_len:
                            if is_terminal(line[next_index]):
                                dataframe.loc[[line[0]], [line[next_index]]] = "[" + str(i) + "]"
                                break
                            else:
                                first_next_index = exe_first_set(line[next_index])
                                if first_next_index:
                                    for j in first_next_index:
                                        dataframe.loc[[line[0]], [j]] = "[" + str(i) + "]"

                        else:
                            follow = exe_follow_set(line[0])
                            if follow:
                                for j in follow:
                                    dataframe.loc[[line[0]], [j]] = "[" + str(i) + "]"
                    else:
                        break

    dataframe = dataframe.fillna("[]")
    print(dataframe)
    return


def update_rhs(line):
    rhs_array = []
    line = line.split(' ')
    line_len = len(line) - 1
    if line[2] != '#':
        for i in range(line_len, 1, -1):
            star_line = just_one(line[i])
            if star_line:
                rh = update_rhs(star_line)
                if rh:
                    rhs_array = rhs_array + rh
            else:
                rhs_array.append(line[i])
    return rhs_array


def just_one(non_terminal):
    global grammar
    read_flag = False
    star_line = ""
    for line in grammar:
        word = line.split(' ')
        if word[0] == non_terminal:
            if not read_flag:
                star_line = line
                read_flag = True
            else:
                return False
    return star_line


grammar = []
non_terminal_tokens_Array = []
terminal_tokens_Array = []
run("grammar.txt")
