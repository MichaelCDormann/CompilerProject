import re

tokens = {}
tokens_temp = {"keyword": ("else", "if", "int", "return", "void", "while", "float"),
			   "symbol": ("+", "-", "*", "/", "//", "<", "<=", ">", ">=", "==", "!=", "=", ";", ",", "(", ")", "[", "]", "{", "}", "/*", "*/")}


def reverse_token_dict():
	global tokens_temp, tokens, token_keys
	for key, values in tokens_temp.iteritems():
		for value in values:
			tokens[value] = key

reverse_token_dict()


class FileAccessManager:

	def __init__(self, filename):
		self.filename = filename

	def open(self):
		return open(self.filename, 'r')

class LexicalAnalyzer:

	comment_counter = 0
	scope_counter = 0
	current_string = ""

	def __init__(self, file_access_wrapper):
		self.file = file_access_wrapper

	def analyze(self):
		token_lexum_tuple = []

		with self.file.open() as f:
			for line in f:

				if re.match("\s", line[-1]) is None:
					line = line + " "

				#if len(line.strip()):
				#	print "\nINPUT: ", line.strip("\n")

				#if self.comment_counter == 0:
				#	line_comment_loc = line.find("//")
				#	other_comment_loc = line.find("/*")
				#	if line_comment_loc != -1 and ((other_comment_loc != -1) ^ (line_comment_loc < other_comment_loc)):
				#		line = line[0:line_comment_loc]

				for character in line:
					result = self.parse(character)
					if result is not None:
						if result == "FlushLine":
							break
						token_lexum_tuple.append(result)

		return token_lexum_tuple

	@staticmethod
	def check_substring(substr):
		for value in tokens.keys():
			if substr in value and substr != value:
				return True
		return False

	@classmethod
	def parse(cls, character):
		lexum = None
		token = None

		#if current_string is empty and character is not a whitespace character and not inside a comment
		if cls.current_string == "" and re.match("\s", character) is None and cls.comment_counter == 0:
			cls.current_string = character
			return None

		cur_string = cls.current_string + character

		#if current_string + the new character is in tokens not a substring of another value in tokens
		if cur_string in tokens and not cls.check_substring(cur_string) and (re.search("[^A-Za-z]+", cur_string) or re.match("[A-Za-z]+", character) is None):
			lexum = tokens[cur_string]
			token = cur_string
			cls.current_string = ""
		#if current_string is in tokens (string without new character)
		elif cls.current_string in tokens and (re.search("[^A-Za-z]+", cur_string) or re.match("[A-Za-z]+", character) is None):
			#since character isn't being used in this lexum, add it to be used in the next(unless it's whitespace)
			lexum = tokens[cls.current_string]
			token = cls.current_string
			cls.current_string = character if re.match("\s", character) is None else ""
		elif re.search("[^A-Za-z]+", cur_string) and re.search("[^0-9.E+-]+", cur_string):
			if re.match("[A-Za-z]+$", cls.current_string) is not None:
				token = "id"
				lexum = cls.current_string
				cls.current_string = character if re.match("\s", character) is None else ""
			elif re.match("[0-9]+$", cls.current_string):
				token = "num"
				lexum = cls.current_string
				cls.current_string = character if re.match("\s", character) is None else ""
			elif re.match("[0-9]+(\.[0-9]+)?(E[+-]?[0-9]+)?$", cls.current_string):
				token = "float"
				lexum = cls.current_string
				cls.current_string = character if re.match("\s", character) is None else ""
			elif len(cls.current_string) > 0:
				if character in tokens or re.match("\s", character):
					#print "ERROR: " + cls.current_string
					cls.current_string = character if re.match("\s", character) is None else ""
					cur_string = cls.current_string

		if lexum == "/*":
			cls.comment_counter += 1
			lexum = None
			cur_string = ""
			character = ""
		elif lexum == "*/" and cls.comment_counter > 0:
			cls.comment_counter -= 1
			lexum = None
			cur_string = ""
			character = ""
		elif lexum == "//" and cls.comment_counter == 0:
			return "FlushLine"
		elif lexum == "{":
			cls.scope_counter += 1
		elif lexum == "}":
			cls.scope_counter -= 1

		#inside a comment
		if cls.comment_counter > 0 and character != "*" and character != "/":
			cls.current_string = ""
			return None
		elif cls.comment_counter > 0 and (character == "*" or character == "/"):
			cls.current_string = character
			return None

		if token is not None and lexum is not None:
			#print "\t{0:10} \t{1:10} \t{2}".format(token, lexum, cls.scope_counter)
			return (token, lexum, cls.scope_counter)
		elif re.match("\s", character) is None:
			cls.current_string = cur_string
		else:
			return None
