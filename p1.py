from LexicalAnalyzer import *

fl = FileAccessManager(sys.argv[1])
analyzer = LexicalAnalyzer(fl)
result = analyzer.analyze()
print result