import re

class SymbolTable(object):

	dict_list = []
	depth = 0

	@classmethod
	def AddItem(cls, name, item):
		if len(cls.dict_list) == 0:
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

		if cls.dict_list[depth][name] is not None:
			return cls.dict_list[depth][name]
		else:
			return cls.GetItem(name, depth-1)

class Var(object):

	def __init__(self, type, value=None, size=None):
		self.type = type
		self.value = value
		self.size = size

class Func(object):

	def __init__(self, ret_type, depth=None, params=[]):
		self.ret_type = ret_type
		self.depth = depth
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

		if self.getParams == True:
			if self.curToken in ["id", "num", "float_num"]:
				self.paramString = self.paramString + self.curLexum + " "
			else:
				self.paramString = self.paramString + self.curToken + " "

		self.index += 1

		if self.index > len(self.token_lexum_list)-1:
			self.curToken = "$"
			return
			#raise IndexError("Index out of range - no more tokens to process")

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
			SymbolTable.AddItem(tokens[1], Func(tokens[0], None, params))
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
		if self.curToken in set(["int", "void", "float"]):
			self.declaration()
			self.declist_prime()
		elif self.curToken in set(["$"]):
			pass
		else:
			raise RejectException("Next token '" + self.curToken + "' not in first(declaration) or follow(declist_prime)")

	def declaration(self):
		if self.curToken in set(["int", "void", "float"]):
			self.Accept()
			self.dec_lf()
		else:
			raise RejectException("Next token was '" + self.curToken + " expected 'int', 'void', or 'float'")

	def dec_lf(self):
		if self.curToken in set(["id"]):
			self.Accept()
			self.dec_lf_lf()
		else:
			raise RejectException("Next token was '" + self.curToken + "' expected 'id'")

	def dec_lf_lf(self):
		if self.curToken in set([";", "["]):
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

		elif self.curToken in set(["("]):
			self.Accept()
			self.getParams = True
			self.params()

			if self.curToken in set([")"]):
				self.InsertST()
				self.Accept()
				self.compoundstmt()
			else:
				raise RejectException("Next token was '" + self.curToken + "' was expecting ')'")

		else:
			raise RejectException("Next token was '" + self.curToken + "' was expecting ';', '[', or '('")

	def params(self):
		if self.curToken in set(["int", "float"]):
			self.Accept()
			if self.curToken == "id":
				self.Accept()
				self.param_lf()
				self.paramlist_prime()
			else:
				raise RejectException("Next token was '" + self.curToken + "' was expecting 'id'")
		elif self.curSymbol == "void":
			self.Accept()
			self.params_lf()
		else:
			raise RejectException("Next token was '" + self.curToken + "' was expecting 'int', 'void' or 'float'")

	def params_lf(self):
		pass

	def paramlist_prime(self):
		pass

	def param(self):
		pass

	def param_lf(self):
		if self.curToken == "[":
			self.Accept()
			if self.curToken == "]":
				self.Accept()
			else:
				raise RejectException("Next token was '" + self.curToken + "' was expecting ']'")
		elif self.curToken in set([")", ","]):  # [")", "[", ","]
			pass
		else:
			raise RejectException("Next token was '" + self.curToken + "' was expecting ')'")

	def compoundstmt(self):
		pass




class RejectException(Exception):
	def __init__(self,*args,**kwargs):
		Exception.__init__(self,*args,**kwargs)