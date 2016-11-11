import re

class SymbolTable(object):

	dict_list = []
	depth = 0

	@classmethod
	def AddItem(cls, name, item):
		if len(cls.dict_list) <= cls.depth:
			cls.dict_list.append({})
		if name not in cls.dict_list[cls.depth]:
			cls.dict_list[cls.depth][name] = item
		else:
			raise RejectException("ID already been declared")

	@classmethod
	def Pop(cls):
		cls.dict_list.pop()
		cls.depth -= 1

		if cls.depth < 0:
			raise IndexError("SymbolTable depth below 0")

	@classmethod
	def IncrementDepth(cls):
		cls.depth += 1
		cls.dict_list.append({})

	@classmethod
	def GetItem(cls, name, depth=None):
		if depth is None:
			depth = cls.depth
		elif depth < 0:
			return None

		if name in cls.dict_list[depth].keys():
			return cls.dict_list[depth][name]
		else:
			return cls.GetItem(name, depth-1)

class Var(object):

	def __init__(self, type, value=None, size=None):
		self.type = type
		self.value = value
		self.size = size

class Func(object):

	def __init__(self, ret_type, params=[]):
		self.ret_type = ret_type
		#self.depth = depth
		self.params = params
		self.param_count = len(params)

class SemanticAnalyzer(object):

	def __init__(self, token_lexum_list):
		self.index = 0
		self.token_lexum_list = token_lexum_list
		self.curToken = self.token_lexum_list[self.index][0]
		self.curLexum = self.token_lexum_list[self.index][1]

		self.curString = ""
		self.getParams = False
		self.paramString = ""

		self.bool_main = False

		self.semmantic_stack = []
		self.func_stack = []
		self.dontpop = False

	def Accept(self):
		if self.curToken == "{":
			SymbolTable.IncrementDepth()
		elif self.curToken == "}":
			SymbolTable.Pop()

		if self.curString.strip().split(" ")[0] in ["float", "int", "void"] or self.curToken in ["float", "int", "void"]:
			if self.curToken in ["id", "num", "float_num"]:
				self.curString = self.curString + self.curLexum + " "
			else:
				self.curString = self.curString + self.curToken + " "

		if self.getParams:
			if self.curToken in ["id", "num", "float_num"]:
				self.paramString = self.paramString + self.curLexum + " "
			else:
				self.paramString = self.paramString + self.curToken + " "

		self.index += 1

		if self.index > len(self.token_lexum_list)-1:
			self.curToken = "$"
			return
			# raise IndexError("Index out of range - no more tokens to process")

		self.curToken = self.token_lexum_list[self.index][0]
		self.curLexum = self.token_lexum_list[self.index][1]

	def InsertST(self):
		self.curString = self.curString.strip()
		if re.match("(int|void|float) [A-Za-z][A-Za-z0-9]* ;", self.curString):
			tokens = self.curString.split(" ")
			if tokens[0] == "void":
				raise RejectException("Invalid type")
			SymbolTable.AddItem(tokens[1], Var(tokens[0]))
			self.curString = ""
		elif re.match("(int|void|float) [A-Za-z][A-Za-z0-9]* " + re.escape("[") + " [0-9]+ " + re.escape("]") +" ;", self.curString):
			tokens = self.curString.split(" ")
			if tokens[0] == "void":
				raise RejectException("Invalid type")
			SymbolTable.AddItem(tokens[1], Var(tokens[0], None, tokens[3]))
			self.curString = ""
		#elif re.match("(int|void|float) [A-Za-z][A-Za-z0-9]* " + re.escape("(") + " ((int|void|float) [A-Za-z][A-Za-z0-9]* (, )?)*" + re.escape(")"), self.curString):
		elif self.getParams == True:
			tokens = self.curString.split(" ")
			params = self.paramString.split(",")
			if tokens[1] == "main" and self.bool_main:
				raise RejectException("main has already been defined")
			elif tokens[1] == "main":
				self.bool_main = True
			func = Func(tokens[0], params)
			SymbolTable.AddItem(tokens[1], func)
			self.func_stack.append(func)
			self.curString = ""
			self.getParams = False

	def Run(self):
		try:
			self.program()
			if self.bool_main:
				return "ACCEPT"
			else:
				return "REJECT"
		except RejectException:
			return "REJECT"
		#self.program()

	#---------------------------------------
	# These methods actually do the parsing
	#---------------------------------------

	def program(self):
		self.declarationlist()

	def declarationlist(self):
		self.declaration()
		self.declist_prime()

	def declist_prime(self):
		if self.curToken in ["int", "void", "float"]:
			self.declaration()
			self.declist_prime()
		elif self.curToken == "$":
			pass
		else:
			raise RejectException("Next token '" + self.curToken + "' not in first(declaration) or follow(declist_prime)")

	def declaration(self):
		if self.curToken in ["int", "void", "float"]:
			self.Accept()
			self.dec_lf()
		else:
			raise RejectException("Next token was '" + self.curToken + " expected 'int', 'void', or 'float'")

	def dec_lf(self):
		if self.curToken == "id":
			if self.curLexum == "main":
				self.func_stack.append("main")
			self.Accept()
			self.dec_lf_lf()
		else:
			raise RejectException("Next token was '" + self.curToken + "' expected 'id'")

	def dec_lf_lf(self):
		if self.curToken in [";", "["]:
			if self.curToken == "[":
				self.Accept()
				if self.curToken == "num":
					self.Accept()
					if self.curToken == "]":
						self.Accept()
						if self.curToken == ";":
							del self.semmantic_stack[:]
							self.Accept()
						else:
							raise RejectException("Next token was '" + self.curToken + "' was expecting ';'")
					else:
						raise RejectException("Next token was '" + self.curToken + "' was expecting ']'")
				else:
					raise RejectException("Next token was '" + self.curToken + "' was expecting 'num'")
			elif self.curToken == ";":
				del self.semmantic_stack[:]
				self.Accept()
			else:
				raise RejectException("Next token was '" + self.curToken + "' was expecting '['")
			self.InsertST()
		elif self.curToken == "(":
			self.Accept()
			self.getParams = True
			self.params()
			if self.curToken == ")":
				self.InsertST()
				self.Accept()
				del self.semmantic_stack[:]
				self.compoundstmt()
			else:
				raise RejectException("Next token was '" + self.curToken + "' was expecting ')'")
		else:
			raise RejectException("Next token was '" + self.curToken + "' was expecting ';', '[', or '('")

	def params(self):
		if self.curToken in ["int", "float"]:
			if len(self.func_stack) > 0:
				if self.func_stack[-1] == "main":
					self.func_stack.pop()
					raise RejectException("Invalid parameters for main function")

			self.Accept()
			if self.curToken == "id":
				self.Accept()
				self.param_lf()
				self.paramlist_prime()
			else:
				raise RejectException("Next token was '" + self.curToken + "' was expecting 'id'")
		elif self.curToken == "void":
			if len(self.func_stack) > 0:
				if self.func_stack[-1] == "main":
					self.func_stack.pop()
			self.Accept()
			self.params_lf()
		else:
			raise RejectException("Next token was '" + self.curToken + "' was expecting 'int', 'void' or 'float'")

	def params_lf(self):
		if self.curToken == "id":
			self.Accept()
			self.param_lf()
			self.paramlist_prime()
		elif self.curToken == ")":
			pass
		else:
			raise RejectException("Next token was '" + self.curToken + "' was expecting 'id' or ')'")

	def paramlist_prime(self):
		if self.curToken == ",":
			self.Accept()
			self.param()
			self.paramlist_prime()
		elif self.curToken == ")":
			pass
		else:
			raise RejectException("Next token was '" + self.curToken + "' was expecting ',' or ')'")

	def param(self):
		if self.curToken in ["int", "void", "float"]:
			self.Accept()
			if self.curToken == "id":
				self.Accept()
				self.param_lf()
			else:
				raise RejectException("Next token was '" + self.curToken + "' was expecting 'id'")
		else:
			raise RejectException("Next token was '" + self.curToken + "' was expecting 'int', 'void' or 'float'")

	def param_lf(self):
		if self.curToken == "[":
			self.Accept()
			if self.curToken == "]":
				self.Accept()
			else:
				raise RejectException("Next token was '" + self.curToken + "' was expecting ']'")
		elif self.curToken in [")", ","]:  # [")", "[", ","]
			pass
		else:
			raise RejectException("Next token was '" + self.curToken + "' was expecting ')'")

	def compoundstmt(self):
		if self.curToken == "{":
			self.Accept()

			del self.semmantic_stack[:]

			if len(self.paramString):
				for param in self.paramString.split(","):
					param = param.strip()
					if param != "void":
						slt = param.split(" ")
						SymbolTable.AddItem(slt[1], Var(slt[0]))

				self.paramString = ""

			self.localdeclarations()
			self.statementlist()
			if self.curToken == "}":

				if len(self.func_stack) != 0 and SymbolTable.depth == 1:
					func = self.func_stack.pop()
					if func.ret_type != "void":
						raise RejectException("Missing return statement")

				self.Accept()
			else:
				raise RejectException("Next token was '" + self.curToken + "' was expecting '}'")
		else:
			raise RejectException("Next token was '" + self.curToken + "' was expecting '{'")

	def localdeclarations(self):
		if self.curToken in ["int", "void", "float"]:
			self.Accept()
			self.dec_lf()
			self.localdeclarations()
		elif self.curToken in ["return", "(", "id", "while", "num", "float_num", ";", "}", "{", "if"]:
			pass
		else:
			raise RejectException(
				"Next token was '" + self.curToken + "' was expecting 'int', 'void', 'float', 'return', '(', 'id', "
				                                     "'while', 'num', 'float_num', ';', '}', '{', or 'if'")

	def statementlist(self):
		if self.curToken in ["return", "(", "while", "num", "float_num", "{", ";", "id", "if"]:
			self.statement()
			self.statementlist()
		elif self.curToken == "}":
			pass
		else:
			raise RejectException(
				"Next token was '" + self.curToken + "' was expecting 'return', '(', 'while', 'num', 'float_num', '{', "
				                                     "';', 'id', or 'if'")

	def statement(self):
		if self.curToken in ["(", ";", "num", "id", "float_num"]:
			self.expressionstmt()
		elif self.curToken == "{":
			self.compoundstmt()
		elif self.curToken == "if":
			self.selectionstmt()
		elif self.curToken == "while":
			self.iterationstmt()
		elif self.curToken == "return":
			self.returnstmt()
		else:
			raise RejectException(
				"Next token was '" + self.curToken + "' was expecting 'return', '(', 'while', 'num', 'float_num', '{', "
				                                     "';', 'id', or 'if'")

	def expressionstmt(self):
		if self.curToken in ["(", "num", "id", "float_num"]:
			self.expression()
			if self.curToken == ";":
				del self.semmantic_stack[:]
				self.Accept()
			else:
				raise RejectException("Next token was '" + self.curToken + "' was expecting ';'")
		elif self.curToken == ";":
			del self.semmantic_stack[:]
			self.Accept()
		else:
			raise RejectException("Next token was '" + self.curToken + "' was expecting '(', 'num', 'id', 'float_num', or ';'")

	def selectionstmt(self):
		if self.curToken == "if":
			self.Accept()
			if self.curToken == "(":
				self.Accept()
				self.expression()
				if self.curToken == ")":
					del self.semmantic_stack[:]
					self.Accept()
					self.statement()
					self.selstmt_lf()
				else:
					raise RejectException("Next token was '" + self.curToken + "' was expecting ')'")
			else:
				raise RejectException("Next token was '" + self.curToken + "' was expecting '('")
		else:
			raise RejectException("Next token was '" + self.curToken + "' was expecting 'if'")

	def selstmt_lf(self):
		if self.curToken == "else":
			self.Accept()
			self.statement()
		elif self.curToken in ["return", "(", "while", "num", "float_num", "{", ";", "}", "id", "if"]:
			pass
		else:
			raise RejectException(
				"Next token was '" + self.curToken + "' was expecting 'return', '(', 'else', 'while', 'num', 'float_num', "
				                                     "'{', ';', '}', 'id', and 'if'")

	def iterationstmt(self):
		if self.curToken == "while":
			self.Accept()
			if self.curToken == "(":
				self.Accept()
				self.expression()
				if self.curToken == ")":
					self.Accept()
					self.statement()
				else:
					raise RejectException("Next token was '" + self.curToken + "' was expecting ')'")
			else:
				raise RejectException("Next token was '" + self.curToken + "' was expecting '('")
		else:
			raise RejectException("Next token was '" + self.curToken + "' was expecting 'while'")

	def returnstmt(self):
		if self.curToken == "return":
			self.Accept()
			self.retstmt_lf()

			ret_type = self.semmantic_stack.pop()
			func = self.func_stack.pop()
			if isinstance(func, Func):
				if func.ret_type != ret_type:
					raise RejectException("Invalid return type")
			else:
				raise RejectException("Invalid use of return")

		else:
			raise RejectException("Next token was '" + self.curToken + "' was expecting 'return'")

	def retstmt_lf(self):
		if self.curToken == ";":
			self.semmantic_stack.append("void")
			self.Accept()
		elif self.curToken in ["(", "num", "id", "float_num"]:
			self.expression()
			if self.curToken == ";":
				self.Accept()
			else:
				raise RejectException("Next token was '" + self.curToken + "' was expecting ';'")
		else:
			raise RejectException("Next token was '" + self.curToken + "' was expecting ';', '(', 'id', 'num', or 'float_num'")

	def expression(self):
		if self.curToken == "id":
			ls = SymbolTable.GetItem(self.curLexum)
			if isinstance(ls, Var):
				self.semmantic_stack.append(ls.type)
			elif isinstance(ls, Func):
				self.semmantic_stack.append(ls)
			else:
				raise RejectException(self.curToken + " has not been defined")
			self.Accept()

			if isinstance(ls, Var):
				if ls.size > 0 and self.curToken != "[":
					raise RejectException("Expected [ for array index")

			self.expr_lf()

			if len(self.semmantic_stack) > 1 and not self.dontpop:
				rs = self.semmantic_stack.pop()
				ls = self.semmantic_stack.pop()

				if ls != rs:
					raise RejectException("Incompatible types")
				elif len(self.semmantic_stack) != 0:
					self.semmantic_stack.append(ls)

		elif self.curToken == "(":
			self.Accept()
			self.expression()
			if self.curToken == ")":
				self.Accept()
				self.term_prime()
				self.addexpr_prime()
				self.simpexpr_lf()
			else:
				raise RejectException("Next token was '" + self.curToken + "' was expecting ')'")
		elif self.curToken in ["num", "float_num"]:
			if self.curToken == "num":
				self.semmantic_stack.append("int")
			elif self.curToken == "float_num":
				self.semmantic_stack.append("float")

			self.Accept()
			self.term_prime()
			self.addexpr_prime()
			self.simpexpr_lf()
		else:
			raise RejectException("Next token was '" + self.curToken + "' was expecting 'id', '(', 'num', or 'float_num'")

	def expr_lf(self):
		if self.curToken in ["[", "<=", ">=", "==", "!=", "+", "*", "-", "/", "=", "<", ">", ")", ";", "]", ","]:
			self.var_lf()
			self.expr_lf_lf()
		elif self.curToken == "(":
			self.Accept()
			self.dontpop = True
			self.args()

			params = []
			while not isinstance(self.semmantic_stack[-1], Func):
				params.append(self.semmantic_stack.pop())
			params.reverse()
			func = self.semmantic_stack.pop()

			if len(params) != func.param_count:
				raise RejectException("Invalid number of parameters")
			else:
				for i in range(0, func.param_count):
					func.params[i] = func.params[i].strip()
					if func.params[i].split(" ")[0] != params[i]:
						raise RejectException("Invalid parameter types")

			self.semmantic_stack.append(func.ret_type)
			self.dontpop = False

			if self.curToken == ")":
				self.Accept()
				self.term_prime()
				self.addexpr_prime()
				self.simpexpr_lf()
			else:
				raise RejectException("Next token was '" + self.curToken + "' was expecting ')'")
		else:
			raise RejectException(
				"Next token was '" + self.curToken + "' was expecting '[', '<=', '>=', '==', '!=', '+', '*', '-', '/', "
				                                     "'=', '<', '>', ')', ';', ']', ',', or '('")

	def expr_lf_lf(self):
		if self.curToken == "=":
			self.Accept()
			self.expression()
		elif self.curToken in ["*", "/", "+", "-", ">=", "==", "<=", "!=", "<", ">", ")", ";", "]", ","]:
			self.term_prime()
			self.addexpr_prime()
			self.simpexpr_lf()
		else:
			raise RejectException(
				"Next token was '" + self.curToken + "' was expecting '*', '/', '+', '-', '>=', '==', '<=', '!=', '<', "
				                                     "'>', ')', ';', ']', ',', or '='")

	def var_lf(self):
		if self.curToken == "[":
			self.Accept()
			self.expression()

			index = self.semmantic_stack.pop()
			if index != "int":
				raise RejectException("Invalid index")

			if self.curToken == "]":
				self.Accept()
			else:
				raise RejectException("Next token was '" + self.curToken + "' was expecting ']'")
		elif self.curToken in ["*", ">=", "]", "==", "=", "+", "<=", "-", ",", "/", ")", ";", "!=", "<", ">"]:
			pass
		else:
			raise RejectException(
				"Next token was '" + self.curToken + "' was expecting '[', '<=', '>=', '==', '!=', '+', '*', '-', '/', "
				                                     "'=', '<', '>', ')', ';', ']', or ','")

	def simpexpr_lf(self):
		if self.curToken in [">=", "==", "<=", "!=", "<", ">"]:
			self.relop()
			self.term()
			self.addexpr_prime()
		elif self.curToken in [")", ";", "]", ","]:
			pass
		else:
			raise RejectException(
				"Next token was '" + self.curToken + "' was expecting '>=', '==', '<=', '!=', '<', '>', ')', ';', ']', or ','")

	def relop(self):
		if self.curToken in ["<=", "<", ">", ">=", "==", "!="]:
			self.Accept()
		else:
			raise RejectException("Next token was '" + self.curToken + "' was expecting '<=', '<', '>', '>=', '==', or '!='")

	def addexpr_prime(self):
		if self.curToken in ["+", "-"]:
			self.addop()
			self.term()

			if len(self.semmantic_stack) % 2 == 0:
				rs = self.semmantic_stack.pop()
				ls = self.semmantic_stack.pop()

				if rs != ls:
					raise RejectException("Type mismatch")

				self.semmantic_stack.append(ls)

			self.addexpr_prime()
		elif self.curToken in [")", ",", ">=", "==", "]", ";", "<=", "!=", "<", ">"]:
			pass
		else:
			raise RejectException(
				"Next token was '" + self.curToken + "' was expecting '+', '-', '<=', '<', '>', '>=', '==', '!=', ')', "
				                                     "',', ']', or ';'")

	def addop(self):
		if self.curToken in ["+", "-"]:
			self.Accept()
		else:
			raise RejectException("Next token was '" + self.curToken + "' was expecting '+', or '-'")

	def term(self):
		if self.curToken in ["(", "num", "id", "float_num"]:
			self.factor()
			self.term_prime()
		else:
			raise RejectException("Next token was '" + self.curToken + "' was expecting '(', 'num', 'id', 'float_num'")

	def term_prime(self):
		if self.curToken in ["*", "/"]:
			self.mulop()
			self.factor()

			if len(self.semmantic_stack) % 2 == 0:
				rs = self.semmantic_stack.pop()
				ls = self.semmantic_stack.pop()
				if ls != rs:
					raise RejectException("Mismatchhed types")

				self.semmantic_stack.append(ls)

			self.term_prime()
		elif self.curToken in [">=", "==", "]", "+", "<=", "-", ",", ")", ";", "!=", "<", ">"]:
			pass
		else:
			raise RejectException(
				"Next token was '" + self.curToken + "' was expecting '*', '/', '>=', '==', ']', '+', '<=', '-', ',', ')', "
				                                     "';', '!=', '<', or '>'")

	def mulop(self):
		if self.curToken in ["*", "/"]:
			self.Accept()
		else:
			raise RejectException("Next token was '" + self.curToken + "' was expecting '*' or '/'")

	def factor(self):
		if self.curToken == "(":
			self.Accept()
			self.expression()
			if self.curToken == ")":
				self.Accept()
			else:
				raise RejectException("Next token was '" + self.curToken + "' was expecting ')'")
		elif self.curToken == "id":
			ls = SymbolTable.GetItem(self.curLexum)
			if isinstance(ls, Var):
				self.semmantic_stack.append(ls.type)
			elif isinstance(ls, Func):
				self.semmantic_stack.append(ls)
			else:
				raise RejectException(self.curToken + " has not been defined")

			self.Accept()

			if isinstance(ls, Var):
				if ls.size > 0 and self.curToken != "[":
					raise RejectException("Expected [ for array index")

			self.factor_lf()
		elif self.curToken in ["num", "float_num"]:
			if self.curToken == "num":
				self.semmantic_stack.append("int")
			elif self.curToken == "float_num":
				self.semmantic_stack.append("float")

			self.Accept()
		else:
			raise RejectException("Next token was '" + self.curToken + "' was expecting '(', 'id', 'num' or 'float_num'")

	def factor_lf(self):
		if self.curToken in ["[", "<=", ">=", "==", "!=", "+", "*", "-", ",", "/", ")", ";", "]", "<", ">"]:
			self.var_lf()
		elif self.curToken == "(":
			self.Accept()
			self.args()

			params = []
			while not isinstance(self.semmantic_stack[-1], Func):
				params.append(self.semmantic_stack.pop())
			func = self.semmantic_stack.pop()

			if len(params) != func.param_count:
				raise RejectException("Invalid number of parameters")
			else:
				for i in range(0, func.param_count):
					if func.params[i].split(" ")[0] != params[i]:
						raise RejectException("Invalid parameter types")

			self.semmantic_stack.append(func.ret_type)

			if self.curToken == ")":
				self.Accept()
			else:
				raise RejectException("Next token was '" + self.curToken + "' was expecting ')'")
		else:
			raise RejectException(
				"Next token was '" + self.curToken + "' was expecting '(', '[', '<=', '>=', '==', '!=', '+', '*', '-', "
				                                     "',', '/', ')', ';', ']', '<', or '>'")

	def args(self):
		if self.curToken in ["(", "num", "id", "float_num"]:
			self.arglist()
		elif self.curToken == ")":
			pass
		else:
			raise RejectException("Next token was '" + self.curToken + "' was expecting '(', 'id', 'num' or 'float_num'")

	def arglist(self):
		self.expression()
		self.arglist_prime()

	def arglist_prime(self):
		if self.curToken == ",":
			self.Accept()
			self.expression()
			self.arglist_prime()
		elif self.curToken == ")":
			pass
		else:
			raise RejectException("Next token was '" + self.curToken + "' was expecting ',' or ')'")


class RejectException(Exception):
	def __init__(self, *args, **kwargs):
		Exception.__init__(self, *args, **kwargs)
