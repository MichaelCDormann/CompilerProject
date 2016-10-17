import re

class SymbolTable(object):

	dict_list = []
	depth = 0

	@classmethod
	def AddItem(cls, name, item):
		if len(cls.dict_list) <= cls.depth:
			cls.dict_list.append({})
		cls.dict_list[cls.depth][name] = item

	@classmethod
	def Pop(cls):
		cls.dict_list.pop()
		cls.depth -= 1

		if cls.depth < 0:
			raise IndexError("SymbolTable depth below 0")

	@classmethod
	def IncrementDepth(cls):
		cls.depth += 1

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

class SyntaxAnalyzer(object):

	def __init__(self, token_lexum_list):
		self.index = 0
		self.token_lexum_list = token_lexum_list
		self.curToken = self.token_lexum_list[self.index][0]
		self.curLexum = self.token_lexum_list[self.index][1]

		self.curString = ""
		self.getParams = False
		self.paramString = ""

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
			SymbolTable.AddItem(tokens[1], Var(tokens[0]))
			self.curString = ""
		elif re.match("(int|void|float) [A-Za-z][A-Za-z0-9]* " + re.escape("[") + " [0-9]+ " + re.escape("]") +" ;", self.curString):
			tokens = self.curString.split(" ")
			SymbolTable.AddItem(tokens[1], Var(tokens[0], None, tokens[3]))
			self.curString = ""
		#elif re.match("(int|void|float) [A-Za-z][A-Za-z0-9]* " + re.escape("(") + " ((int|void|float) [A-Za-z][A-Za-z0-9]* (, )?)*" + re.escape(")"), self.curString):
		elif self.getParams == True:
			tokens = self.curString.split(" ")
			params = self.paramString.split(",")
			SymbolTable.AddItem(tokens[1], Func(tokens[0], params))
			self.curString = ""
			self.paramString = ""
			self.getParams = False

	def Run(self):
		#try:
		#	self.program()
		#	print "ACCEPT"
		#except RejectException:
		#	print "REJECT"
		self.program()

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
							self.Accept()
						else:
							raise RejectException("Next token was '" + self.curToken + "' was expecting ';'")
					else:
						raise RejectException("Next token was '" + self.curToken + "' was expecting ']'")
				else:
					raise RejectException("Next token was '" + self.curToken + "' was expecting 'num'")
			elif self.curToken == ";":
				self.Accept()
			else:
				raise RejectException("Next token was '" + self.curToken + "' was expecting '[' or ';'")
			self.InsertST()

		elif self.curToken == "(":
			self.Accept()
			self.getParams = True
			self.params()

			if self.curToken == ")":
				self.InsertST()
				self.Accept()
				self.compoundstmt()
			else:
				raise RejectException("Next token was '" + self.curToken + "' was expecting ')'")

		else:
			raise RejectException("Next token was '" + self.curToken + "' was expecting ';', '[', or '('")

	def params(self):
		if self.curToken in ["int", "float"]:
			self.Accept()
			if self.curToken == "id":
				self.Accept()
				self.param_lf()
				self.paramlist_prime()
			else:
				raise RejectException("Next token was '" + self.curToken + "' was expecting 'id'")
		elif self.curToken == "void":
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
			self.localdeclarations()
			self.statementlist()
			if self.curToken == "}":
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
				self.Accept()
			else:
				raise RejectException("Next token was '" + self.curToken + "' was expecting ';'")
		elif self.curToken == ";":
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

	def expression(self):
		self.Accept()

class RejectException(Exception):
	def __init__(self,*args,**kwargs):
		Exception.__init__(self,*args,**kwargs)