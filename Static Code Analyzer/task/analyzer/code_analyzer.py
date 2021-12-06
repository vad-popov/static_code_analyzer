# write your code here
import re
import sys
import os
import ast

args = sys.argv
file_or_dir = args[1]

''' line_parse will become a list of dictionaries of the following format
[{type: 'mlcomment' or 'comment' or 'string' or 'normal'
  text: some text without separator}
]
This will allow us to ignore text lines or comments in most of our checks 
    and use normal "contains" function for all validations

Parsing logics:
process every line to get tokens of text in a dictionary
({'type': normal or comment or mlcomment or strings
   'text': token text})
after that it's handy to process only 'normal' text not to mix it with comments or strings

1) look for multiline separators, if any - add to the list with the remaining part
2) look for strings, if any - add to list (process correctly '' or "" casaes) with 
the remaining part
3)  add "normal" part to the list
4) apply all normal part validations
5) update prev_multiline_comment and prev_multiline_sep for multiline 
separator cases for future lines and go to nextline processing

'''
def check_snakecese(text):
    r = re.search(r'[A-Z]', text)
    if r:
        return False
    else:
        return True

# [S010] Argument name arg_name should be  written in snake_case;
# [S011] Variable var_name should be written in snake_case;
# [S012] The default argument value is mutable.
def ast_based_checks(ast_tree, file_lines, error_dict):

    for node in ast.walk(ast_tree):

        if isinstance(node, ast.FunctionDef):
            if not check_snakecese(node.name):
                    def_line_num = node.lineno
                    body_line_num = node.body[0].lineno
                    for i in range(node.lineno, node.body[0].lineno):
                        if 'def' in file_lines[i-1].lower():
                            def_line_num = i
                            break
                    error_dict[(def_line_num, 'S009')] = f"S009 Function name '{node.name}' should use snake_case"

            # [S010] Argument name arg_name should be  written in snake_case;
            for a in node.args.args:
                if not check_snakecese(a.arg):
                    error_dict[(a.lineno, 'S010')] = f"S010 Argument name '{a.arg}' should be  written in snake_case"

            # [S012] The default argument value is mutable
            for def_arg in node.args.defaults:
                if isinstance(def_arg, (ast.List, ast.Dict, ast.Set)):
                    error_dict[(def_arg.lineno, 'S012')] = f'S012 The default argument value is mutable'

        if isinstance(node, ast.Assign):
            # [S011] Variable var_name should be written in snake_case;
            for target in node.targets:
                try:
                    if not check_snakecese(target.id):
                        error_dict[(target.lineno, 'S011')] = f"S011 Variable '{target.id}' should be written in snake_case"
                except AttributeError:
                    pass

ESCAPES = ((r'\\', '%%BWSLASH%%'), (r"\'", '%%QUOTE1%%'), (r'\"', '%%QUOTE2%%'))


# let's escape sequences of \\ or \' or \" not to get them processed by normal strings split operation
def encode_escapes(str_1):
    str_2 = str_1
    for i in ESCAPES:
        str_2 = str_2.replace(i[0], i[1])
    return str_2


# decode original sequences
def decode_escapes(str_1):
    str_2 = str_1
    for i in ESCAPES:
        str_2 = str_2.replace(i[1], i[0])
    return str_2


def check_indentation(file_line):
    if re.match(r'^(\s{4})*?([\S].*?)?$', file_line):
        return True
    else:
        return False

def get_multispaces_word(file_line):
    r = re.search(r'(def|class)\s{2,}', file_line)
    if r:
        return r.group()
    else:
        return None

def get_bad_classname(file_line):
    r = re.search(r'class\s+.*?_.*?(\(|:)', file_line)
    if r:
        w = r.group().split(' ',2)[1].strip().rstrip('(:')
        return(w)
    r = re.search(r'class\s+[a-z].*?(\(|:)', file_line)
    if r:
        w = r.group().split(' ',2)[1].strip().rstrip('(:')
        return(w)
    else:
        return None


def get_bad_function(file_line):
    r = re.search(r'def\s+.*?[A-Z].*?(\(|:)', file_line)
    if r:
        w = r.group().split(' ', 2)[1].strip().rstrip('(:')
        return (w)
    else:
        return None

# Get separator with minimum position (to find 1st occurence of (''' or """), (' or ") - etc)
def get_min_sep(file_line, *args):
    sep_positions = {s: file_line.find(s) for s in args if file_line.find(s) >= 0}
    if sep_positions:
        # print(sep_positions)
        return min(sep_positions, key=sep_positions.get)
    else:
        return None


# take string from unprocessed part till separator (or till end of line)
# and put it to previous part of certain type
def add_token(list, type, sep):
    if sep:
        split_tokens = list[-1]['text'].split(sep, maxsplit=1)
    else:
        split_tokens = [list[-1]['text']]

    list.insert(-1, {"type": type, "text": split_tokens[0]})

    if len(split_tokens) < 2:
        list[-1]['text'] = ""
    else:
        list[-1]['text'] = split_tokens[1]
    return split_tokens


def parse_new_line(file_line, line_tokens=[], prev_multiline_sep=""):
    # start parsing, create 1st record in tokens list
    if not line_tokens:  # empty tokens list - 1st run
        line_tokens.append({"type": 'unprocessed', "text": file_line})

    # if this is a multiline comment - find next separator of previous multiline
    # while there is something to parse
    next_sep = ""
    while line_tokens[-1]['text']:

        # handle ending of previous multiline comments first
        if prev_multiline_sep:
            split_tokens = add_token(line_tokens, 'mlcomment', prev_multiline_sep)

            if len(split_tokens) == 1:
                # no separator till the end of line - whole line reminder should become a comment
                return True
            else:
                prev_multiline_sep = ''
                continue

        # continue with other separators
        if not next_sep:
            # try to find next separator
            next_sep = get_min_sep(line_tokens[-1]['text'], '"""', "'''", '"', "'", '#')
            if not next_sep:
                # convert last piece to "normal" text and return
                add_token(line_tokens, 'normal', '')
                return True
            else:
                # add new "normal" token - text before specific separators
                split_tokens = add_token(line_tokens, 'normal', next_sep)
        elif next_sep in ("'''", '"""'):
            prev_multiline_sep = next_sep
            next_sep = ""
            continue
        elif next_sep in ("'", '"'):
            split_tokens = add_token(line_tokens, 'string', next_sep)
            next_sep = ""
            continue
        elif next_sep == '#':
            # convert last piece to "comment" text and return - whole line reminder should become a comment
            add_token(line_tokens, 'comment', '')
            return True


def check_one_file(file_name):
    empty_counter = 0
    with open(file_name, 'r') as file_:
        file_lines = file_.readlines()
        ast_tree = ast.parse(''.join(file_lines))
        error_dict = {}  # dictionary {(<line_num>, 'err_code like S010'), 'err_text like S01 error'}

        # [S010] Argument name arg_name should be  written in snake_case;
        # [S011] Variable var_name should be written in snake_case;
        # [S012] The default argument value is mutable.
        ast_based_checks(ast_tree, file_lines, error_dict)

        for line_num, line in enumerate(file_lines, start=1):
            # print(line_num, line)
            line_tokens = []
            prev_multiline_sep = ''
            line_encoded = encode_escapes(line)
            parse_new_line(line_encoded, line_tokens, prev_multiline_sep)

            for i in line_tokens:
                i['text'] = decode_escapes(i['text'])

            if len(line) > 79:
                print(f"{file_name}: Line {line_num}: S001 The line is too long")
            if not check_indentation(line):
                print(f"{file_name}: Line {line_num}: S002 Indentation is not a multiple of four")
            # check for semicolon in "normal" text
            if ';' in (''.join([i['text'] for i in line_tokens if i['type'] == 'normal'])):
                print(
                    f"{file_name}: Line {line_num}: S003 Unnecessary semicolon after a statement (note that semicolons are acceptable in comments")
            if line[0] != '#' \
                    and len(line_tokens) > 2 and line_tokens[-2]['type'] == 'comment' \
                    and (line_tokens[-3]['type'] != 'normal' \
                         or line_tokens[-3]['type'] == 'normal' \
                         and line_tokens[-3]['text'][-2:] != '  '):
                print(f"{file_name}: Line {line_num}: S004 Less than two spaces before inline comments")

            if 'TODO' in ''.join([i['text'].upper() for i in line_tokens if i['type'] == 'comment']):
                print(f"{file_name}: Line {line_num}: S005 TODO found (in comments only and case-insensitive)")
            if line == '\n':
                empty_counter += 1
            else:
                if empty_counter > 2:
                    print(
                        f"{file_name}: Line {line_num}: S006 More than two blank lines preceding a code line (applies to the first non-empty line")
                empty_counter = 0
            multi_space_word = get_multispaces_word(line)
            if multi_space_word:
                print(f"{file_name}: Line {line_num}: S007 Too many spaces after construction_name '{multi_space_word.strip()}'")
            class_name = get_bad_classname(line)
            if class_name:
                print(f"{file_name}: Line {line_num}: S008 Class name '{class_name}' should be written in CamelCase")
            #function_name = get_bad_function(line)
            #if function_name:
            #    print(f"{file_name}: Line {line_num}: S009 Function name '{function_name}' should use snake_case")
            if (line_num, 'S009') in error_dict:
                print(f"{file_name}: Line {line_num}: {error_dict[(line_num, 'S009')]}")
            if (line_num, 'S010') in error_dict:
                print(f"{file_name}: Line {line_num}: {error_dict[(line_num, 'S010')]}")
            if (line_num, 'S011') in error_dict:
                print(f"{file_name}: Line {line_num}: {error_dict[(line_num, 'S011')]}")
            if (line_num, 'S012') in error_dict:
                print(f"{file_name}: Line {line_num}: {error_dict[(line_num, 'S012')]}")

# main part starts here

if os.path.isfile(file_or_dir):
    check_one_file(file_or_dir)
elif os.path.isdir(file_or_dir):
    files = [os.path.join(file_or_dir, f) for f in os.listdir(path=file_or_dir) if f.endswith('.py')]
    for file_name in files:
        check_one_file(file_name)




