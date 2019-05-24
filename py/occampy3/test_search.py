import sys
import heapq
import time
sys.path.insert(0, "./wrappers")

from search import Search
from utils import CLIUtils

search = Search.init_from_command_line(sys.argv[0:2])
CLIUtils.print_basic_statics(solver=search)
search.execute()