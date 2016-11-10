import sys
from LexicalAnalyzer.LexicalAnalyzer import *
from SemanticAnalyzer import *

fl = FileAccessManager(sys.argv[1])
analyzer = LexicalAnalyzer(fl)
result = analyzer.analyze()

semanter = SemanticAnalyzer(result)
run_result = semanter.Run()

#print result

print run_result