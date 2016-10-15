

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


