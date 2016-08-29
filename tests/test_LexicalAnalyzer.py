from LexicalAnalyzer import *
import io

def test_reverse_token_dict():
    reversed_dict = {"else": "keyword", "if": "keyword", "int": "keyword", "return": "keyword", "void": "keyword", "while": "keyword", "float": "keyword",
               "+": "symbol", "-": "symbol", "*": "symbol", "/": "symbol", "//": "symbol", "<": "symbol", "<=": "symbol", ">": "symbol", ">=": "symbol", "==": "symbol", "!=": "symbol", "=": "symbol", ";": "symbol", ",": "symbol", "(": "symbol", ")": "symbol", "[": "symbol", "]": "symbol", "{": "symbol", "}": "symbol", "/*": "symbol", "*/": "symbol"}
    reverse_token_dict()
    assert tokens == reversed_dict

def test_parse():
    output = [("keyword", "int", 0)]

    fake_file = FakeFile("int")
    analyzer = LexicalAnalyzer(fake_file)
    result = analyzer.analyze()

    assert result == output


class FakeFile:

    def __init__(self, text):
        self.text = text

    def open(self):
        return io.StringIO(self.text)