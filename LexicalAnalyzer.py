
tokens = {}
tokens_temp = {"keyword": ("else", "if", "int", "return", "void", "while", "float"),
               "symbol": ("+", "-", "*", "/", "<", "<=", ">", ">=", "==", "!=", "=", ";", ",", "(", ")", "[", "]", "{", "}", "/*", "*/")}
num = [i for i in range(0,9)]
id = [chr(i) for i in range(65, 122) if not (90 < i < 97)]


def reverse_token_dict():
    global tokens_temp, tokens
    for key, values in tokens_temp.iteritems():
        for value in values:
           tokens[value] = key

reverse_token_dict()

