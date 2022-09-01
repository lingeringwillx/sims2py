import sys

if sys.maxsize > 2 ** 32:
    from dbpf64 import *
else:
    from dbpf32 import *