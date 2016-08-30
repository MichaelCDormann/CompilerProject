import re
import sys

tokens = {}
tokens_temp = {"keyword": ("else", "if", "int", "return", "void", "while", "float"),
               "symbol": ("+", "-", "*", "/", "//", "<", "<=", ">", ">=", "==", "!=", "=", ";", ",", "(", ")", "[", "]", "{", "}", "/*", "*/")}


def reverse_token_dict():
    global tokens_temp, tokens, token_keys
    for key, values in tokens_temp.iteritems():
        for value in values:
           tokens[value] = key

reverse_token_dict()


class FileAccessManager:

    def __init__(self, filename):
        self.filename = filename

    def open(self):
        return open(self.filename, 'r')

class LexicalAnalyzer:

    comment_counter = 0
    scope_counter = 0
    current_string = ""

    def __init__(self, file_access_wrapper):
        self.file = file_access_wrapper

    def analyze(self):
        token_lexum_tuple = []

        with self.file.open() as f:
            for line in f:
                line = line.strip('\n') + " "
                print "INPUT: " + line.strip('\n')

                for character in line:
                    result = self.parse(character)
                    if result is not None:
                        token_lexum_tuple.append(result)

        return token_lexum_tuple

    @staticmethod
    def check_substring(substr):
        for value in tokens.keys():
            if substr in value and substr != value:
                return True
        return False

    @classmethod
    def parse(cls, character):
        lexum = None
        token = None

        #if current_string is empty and character is not a whitespace character and not inside a comment
        if cls.current_string == "" and re.match("\s", character) is None and cls.comment_counter == 0:
            cls.current_string = character
            return None

        cur_string = cls.current_string + character

        #if current_string + the new character is in tokens not a substring of another value in tokens
        if cur_string in tokens and not cls.check_substring(cur_string):
            token = tokens[cur_string]
            lexum = cur_string
            cls.current_string = ""
        #if current_string is in tokens (string without new character)
        elif cls.current_string in tokens:
            #since character isn't being used in this lexum, add it to be used in the next(unless it's whitespace)
            token = tokens[cls.current_string]
            lexum = cls.current_string
            cls.current_string = character if re.match("\s", character) is None else ""
        #elif re.match("\s", character) is not None:
        elif re.search("[^A-Za-z0-9]+", cur_string):
            if re.match("[A-Za-z]+", cls.current_string):
                token = "ID"
                lexum = cls.current_string
                cls.current_string = character if re.match("\s", character) is None else ""
            elif re.match("[0-9]+", cls.current_string):
                token = "Num"
                lexum = cls.current_string
                cls.current_string = character if re.match("\s", character) is None else ""
            elif len(cls.current_string) > 0:
                print "ERROR: " + cls.current_string + " not in grammar"
                cls.current_string = ""

        if lexum == "/*":
            cls.comment_counter += 1
            lexum = None
            cur_string = ""
            character = ""
        elif lexum == "*/":
            cls.comment_counter -= 1
            lexum = None
            cur_string = ""
            character = ""
        elif lexum == "{":
            cls.scope_counter += 1
        elif lexum == "}":
            cls.scope_counter -= 1

        #inside a comment
        if cls.comment_counter > 0 and character != "*" and character != "/":
            cls.current_string = ""
            return None
        elif cls.comment_counter > 0 and (character == "*" or character == "/"):
            cls.current_string = character
            return None

        if token is not None and lexum is not None:
            print token + ": " + lexum
            return (token, lexum, cls.scope_counter)
        elif re.match("\s", character) is None:
            cls.current_string = cur_string
        else:
            return None
