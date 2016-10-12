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


terminals = ["a", "h", "b", "c", "g", "m", "d", "empty"]
grammar = collections.OrderedDict([
	("S",   ["a X"]),
	("X",   ["E Y"]),
	("Y",   ["F B h", "b"]),
	("B",   ["c C"]),
	("C",   ["b C", "empty"]),
	("E",   ["g", "empty"]),
	("F",   ["m F'", "F'"]),
	("F'",  ["d F'", "empty"])
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
		original_rule = expr
		firsts = set()
		expressions = grammar[expr]
		for expr in expressions:
			lexums = expr.split(" ")
			firsts = firsts.union(get_first(lexums[0]))
			index = 1
			while "empty" in firsts and index < len(lexums) and original_rule != lexums[index]:
				firsts = firsts.difference(set(["empty"]))
				firsts = firsts.union(get_first(lexums[index]))
				index = index + 1

		return firsts

def calc_follow():
	first_rule = grammar.keys()[0]
	follow[first_rule] = set(["$"])

	lexum_list = []
	for expressions in grammar.itervalues():
		for expr in expressions:
			lexums = expr.split(" ")
			if len(lexums) > 1:
				lexum_list.append(lexums)

	for lexums in lexum_list:
		get_follow(lexums)

	iterate = True
	while iterate:
		iterate = False
		for rule, expressions in grammar.iteritems():
			for expr in expressions:
				lexums = expr.split(" ")
				last_lexum = lexums[-1]

				if last_lexum in terminals:
					continue

				if last_lexum in follow.keys():
					if follow[last_lexum].intersection(follow[rule]) != follow[rule]:
						follow[last_lexum] = follow[last_lexum].union(follow[rule])
						iterate = True
				else:
					follow[last_lexum] = follow[rule]
					iterate = True

				for i in range(0, len(lexums)):
					if "empty" not in first[last_lexum]:
						break
					last_lexum = lexums[lexums.index(last_lexum) - 1]
					if last_lexum in terminals:
						break
					if last_lexum in follow.keys():
						if follow[last_lexum].intersection(follow[rule]) != follow[rule]:
							follow[last_lexum] = follow[last_lexum].union(follow[rule])
							iterate = True
					else:
						follow[last_lexum] = follow[rule]
						iterate = True

def get_follow(lexums):
	for i in range(0, len(lexums)):
		if lexums[i] not in terminals:
			follow_set = set()

			try:
				if lexums[i+1] in terminals:
					follow_set.add(lexums[i+1])
				else:
					follow_set = follow_set.union(first[lexums[i+1]])
					index = i + 1
					while "empty" in follow_set and index < len(lexums):
						follow_set = follow_set.difference(set(["empty"]))
						if lexums[index + 1] in terminals:
							follow_set = follow_set.add(lexums[index + 1])
						else:
							follow_set = follow_set.union(first[lexums[index + 1]])
						index = index + 1

					follow_set = follow_set.difference(set(["empty"]))

				if lexums[i] in follow.keys():
					follow[lexums[i]] = follow[lexums[i]].union(follow_set)
				else:
					follow[lexums[i]] = follow_set
			except:
				continue

calc_first()
print first
calc_follow()
print follow