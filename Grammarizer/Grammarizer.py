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
		#for each rule, expression pair. Example: A -> BC | e    A is the rule, BC | e is the expression
		first_set = set()
		for expr in expressions:
			#for each sub-expression. Example: "BC" is one and "e" is another
			lexums = expr.split(" ")
			first_set = first_set.union(get_first(lexums[0]))
			index = 1
			while "empty" in first_set and index < len(lexums):
				#if there is an empty in the first set get the first set of the next lexum as well
				first_set = first_set.difference(set(["empty"]))
				first_set = first_set.union(get_first(lexums[index]))
				index = index + 1

		#store rule and it's first set
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
				#if there is an empty in the first set get the first set of the next rule as well, unless the next rule is the original rule
				#that we are trying to find the first set of (to avoid an infinite loop)
				firsts = firsts.difference(set(["empty"]))
				firsts = firsts.union(get_first(lexums[index]))
				index = index + 1

		return firsts

def calc_follow():
	#add "$" to follow of start rule
	first_rule = grammar.keys()[0]
	follow[first_rule] = set(["$"])

	#create a list of lexum lists based on each production rule - easier to use this data later
	lexum_list = []
	for expressions in grammar.itervalues():
		for expr in expressions:
			lexums = expr.split(" ")
			if len(lexums) > 1:
				lexum_list.append(lexums)

	#pass each list of lexums to the next function
	for lexums in lexum_list:
		get_follow(lexums)

	#iteratively add the left rule's follows to the right most production's follows
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
						# if the follow of the right rule isn't in the follow of the left production
						follow[last_lexum] = follow[last_lexum].union(follow[rule])
						iterate = True
				else:
					follow[last_lexum] = follow[rule]
					iterate = True

				#go through the remaining rules, right to left, to account for emptys
				for i in range(len(lexums)-1, 0, -1):
					if "empty" not in first[last_lexum]:
						break
					last_lexum = lexums[i]
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
				#figure out what to do with the next lexum - if it's a terminal add it to the follow set
				if lexums[i+1] in terminals:
					follow_set.add(lexums[i+1])
				else:
					#otherwie get the first set of the next lexum and add it to the follow set
					follow_set = follow_set.union(first[lexums[i+1]])
					index = i + 1
					while "empty" in follow_set and index < len(lexums):
						#while there is an empty in the follow set get the first set of the next lexum as well
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