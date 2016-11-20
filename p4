#!/usr/bin/python

import sys
from LexicalAnalyzer.LexicalAnalyzer import *
from CodeGenerator import *

fl = FileAccessManager(sys.argv[1])
analyzer = LexicalAnalyzer(fl)
result = analyzer.analyze()

generator = CodeGenerator(result)
run_result = generator.Run()

print run_result