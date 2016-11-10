import os
import re
import pytest

from LexicalAnalyzer.LexicalAnalyzer import *
from SemanticAnalyzer import *

testdata = []

files = os.listdir("./SemanticTests")

for file in files:
	if re.match("test[0-9]+.txt", file):
		file = "./SemanticTests/" + file
		with open(file, 'r') as openfile:
			lines = openfile.readlines()
			firstline = lines[0]
			if re.search("accept", firstline):
				ex_result = "ACCEPT"
			else:
				ex_result = "REJECT"

		testdata.append((file, ex_result))

@pytest.mark.parametrize("file, exp_result", testdata)
def test_syntaxanalyzer(file, exp_result):

	print file, exp_result

	fl = FileAccessManager(file)
	analyzer = LexicalAnalyzer(fl)
	result = analyzer.analyze()

	semanter = SemanticAnalyzer(result)
	run_result = semanter.Run()

	print result

	assert run_result == exp_result