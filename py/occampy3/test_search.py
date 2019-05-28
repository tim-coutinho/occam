import sys
import heapq
import time
sys.path.insert(0, "./wrappers")

from search import Search

search = Search("VB")
search.execute(sys.argv[0:2])
