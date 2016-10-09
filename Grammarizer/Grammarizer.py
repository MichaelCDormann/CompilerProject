import collections

terminals = ["id", ";", "[", "]", "num", "int", "void", "float", "(", ")", ",", "{", "}", "if", "else", "while",
             "return", "=", "<=", "<", ">", ">=", "==", "!=", "+", "-", "*", "/"]
grammar = collections.OrderedDict([
	("program",              ["declaration-list"]),
	("declaration-list",     ["declaration-list declaration", "declaration"]),
	("declaration",          ["var-declaration", "fun-declaration"]),
	("var-declaration",      ["type-specifier id ;", "type-specifier id [ num ] ;"]),
	("type-specifier",       ["int", "void", "float"]),
	("fun-declaration",      ["type-specifier id ( params ) compound-stmt"]),
	("params",               ["param-list", "void"]),
	("param-list",           ["param-list , param", "param"]),
	("param",                ["type-specifier id", "type-specifier id [ ]"]),
	("compound-stmt",        ["{ local-declarations statement-list }"]),
	("local-declarations",   ["local-declarations var-declaration", "empty"]),
	("statement-list",       ["statement-list statement", "empty"]),
	("statement",            ["expression-stmt", "compound-stmt", "selection-stmt", "iteration-stmt", "return-stmt"]),
	("expression-stmt",      ["expression ;", ";"]),
	("selection-stmt",       ["if ( expression ) statement", "if ( expression ) statement else statement"]),
	("iteration-stmt",       ["while ( expression ) statement"]),
	("return-stmt",          ["return ;", "return expression ;"]),
	("expression",           ["var = expression", "simple-expression"]),
	("var",                  ["id", "id [ expression ]"]),
	("simple-expression",    ["additive-expression relop additive-expression", "additive-expression"]),
	("relop",                ["<=", "<", ">", ">=", "==", "!="]),
	("additive-expression",  ["additive-expression addop term", "term"]),
	("addop",                ["+", "-"]),
	("term",                 ["term mulop factor", "factor"]),
	("mulop",                ["*", "/"]),
	("factor",               ["( expression )", "var", "call", "num", "float"]),
	("call",                 ["id ( args )"]),
	("args",                 ["arg-list", "empty"]),
	("arg-list",             ["arg-list , expression", "expression"])
])

first = {}
follow = {}

def print_grammar():
	for rule, expression in grammar.iteritems():
		expr_string = ""
		for i in  range(0, len(expression)):
			expr_string = expr_string + expression[i] + (" | " if (len(expression) > 1 and len(expression) - 1 != i) else "")
		print "{0:20} ->   {1}".format(rule, expr_string)

def left_factor():

