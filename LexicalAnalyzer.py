import re
import sys

tokens = {}
tokens_temp = {"keyword": ("else", "if", "int", "return", "void", "while", "float"),
               "symbol": ("+", "-", "*", "/", "//", "<", "<=", ">", ">=", "==", "!=", "=", ";", ",", "(", ")", "[", "]", "{", "}", "/*", "*/")}

num = [i for i in range(0,9)]
id = [chr(i) for i in range(65, 122) if not (90 < i < 97)]


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


class Printer:

    def __init__(self, text):
        self.text = text

    def add(self, text):
        self.text += text

    def addLine(self, text):
        self.text = self.text + "\n" + text

    def prnt(self):
        print self.text
        self.text = ""


class LexicalAnalyzer:

    comment_counter = 0
    scope_counter = 0
    current_string = ""

    def __init__(self, file_access_wrapper):
        self.file = file_access_wrapper
        self.printer = Printer("")

    def analyze(self):
        with self.file.open() as f:
            line = f.readline()
            self.printer.addLine("INPUT: " + line)

            for character in line:
                result = self.parse(character)
                if result is not None:
                    self.printer.addLine(result)

        return self.printer

    @staticmethod
    def check_substring_in_list(substr, lst):
        for value in lst:
            if substr in value and substr != value:
                return True
        return False

    @classmethod
    def parse(cls, character):
        cls.current_string += character

        if cls.current_string in tokens and not cls.check_substring_in_list(cls.current_string, tokens.keys()):
            return "" + tokens[cls.current_string] + ": " + cls.current_string


#fl = FileAccessManager(sys.argv[1])
#analyzer = LexicalAnalyzer(fl)
#analyzer.analyze()