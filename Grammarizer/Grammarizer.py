import collections

#terminals = ["id", ";", "[", "]", "num", "int", "void", "float", "(", ")", ",", "{", "}", "if", "else", "while",
#             "return", "=", "<=", "<", ">", ">=", "==", "!=", "+", "-", "*", "/"]
"""grammar = collections.OrderedDict([
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
])"""


terminals = ["a", "b", "c", "e", "f", "g", "empty"]
grammar = collections.OrderedDict([
	("S",   ["A B C D E"]),
	("A",   ["a b A", "a b", "c", "empty"]),
	("B",   ["C a", "D g", "empty"]),
	("C",   ["b"]),
	("D",   ["e", "empty"]),
	("E",   ["f"])
])

first = collections.OrderedDict({})
follow = collections.OrderedDict({})

def print_grammar():
	for rule, expression in grammar.iteritems():
		expr_string = ""
		for i in  range(0, len(expression)):
			expr_string = expr_string + expression[i] + (" | " if (len(expression) > 1 and len(expression) - 1 != i) else "")
		print "{0:20} ->   {1}".format(rule, expr_string)

def calc_first():
	for rule, expressions in grammar.iteritems():
		first_set = set()
		for expr in expressions:
			lexums = expr.split(" ")
			first_set = first_set.union(get_first(lexums[0]))
			index = 1
			while "empty" in first_set and index < len(lexums):
				first_set = first_set.difference(set(["empty"]))
				first_set = first_set.union(get_first(lexums[index]))
				index = index + 1

		first[rule] = first_set

def get_first(expr):
	if expr in terminals:
		return set([expr])
	else:
		firsts = set()
		expressions = grammar[expr]
		for expr in expressions:
			lexums = expr.split(" ")
			firsts = firsts.union(get_first(lexums[0]))
			index = 1
			while "empty" in firsts and index < len(lexums):
				firsts = firsts.difference(set(["empty"]))
				firsts = firsts.union(get_first(lexums[index]))
				index = index + 1

		return firsts

calc_first()
print first