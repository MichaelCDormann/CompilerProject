from LexicalAnalyzer import *

def test_reverse_token_dict():
    reversed_dict = {"else": "keyword", "if": "keyword", "int": "keyword", "return": "keyword", "void": "keyword", "while": "keyword", "float": "keyword",
               "+": "symbol", "-": "symbol", "*": "symbol", "/": "symbol", "<": "symbol", "<=": "symbol", ">": "symbol", ">=": "symbol", "==": "symbol", "!=": "symbol", "=": "symbol", ";": "symbol", ",": "symbol", "(": "symbol", ")": "symbol", "[": "symbol", "]": "symbol", "{": "symbol", "}": "symbol", "/*": "symbol", "*/": "symbol"}
    reverse_token_dict()
    assert tokens == reversed_dict