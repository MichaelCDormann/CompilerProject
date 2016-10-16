class SymbolTalble(object):

	dict_list = []
	depth = 0

	@classmethod
	def AddItem(cls, name, item):
		if cls.dict_list[cls.depth] is None:
			cls.dict_list[cls.depth] = {}
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
	def GetItem(cls, name, depth):
		if depth is None:
			depth = cls.depth
		elif depth < 0:
			return None

		if cls.dict_list[depth][name] is not None:
			return cls.dict_list[depth][name]
		else:
			return cls.GetItem(name, depth-1)

class Num(object):

	def __init__(self, name, value):
		self.name = name
		self.value = value

class Float(object):

	def __init__(self, name, value):
		self.name = name
		self.value = value

class Func(object):

	def __init__(self, name, ret_type, depth, params):
		self.name = name
		self.ret_type = ret_type
		self.depth = depth
		self.params = params
		self.param_count = len(params)

class SyntaxAnalyzer(object):

	def __init__(self, token_lexum_list):
		self._index = 0
		self._token_lexum_list = token_lexum_list
		self._curToken = self.token_lexum_list[self.index][0]
		self._curLexum = self.token_lexum_list[self.index][1]

	def Accept(self):
		self.index += 1

		if self.index > len(self.token_lexum_list)-1:
			self.curToken = "$"
			return
			#raise IndexError("Index out of range - no more tokens to process")

		self.curToken = self.token_lexum_list[self.index][0]
		self.curLexum = self.token_lexum_list[self.index][1]

	def Run(self):
		#try:
		#	self.program()
		#	print "ACCEPT"
		#except RejectException:
		#	print "REJECT"
		#self.program()

	@property
	def curToken(self):
		return self._curToken

	@property
	def curLexum(self):
		return self._curLexum

	@property
	def index(self):
		return self._index

	@property
	def token_lexum_list(self):
		return self._token_lexum_list

	@curToken.setter
	def curToken(self, value):
		self._curToken = value

	@curLexum.setter
	def curLexum(self, value):
		self._curLexum = value

	@index.setter
	def index(self, value):
		self._index = value

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
		pass

class RejectException(Exception):
	def __init__(self,*args,**kwargs):
		Exception.__init__(self,*args,**kwargs)