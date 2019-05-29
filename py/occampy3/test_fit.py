import sys
sys.path.insert(0, "./wrappers")

from fit import Fit
from utils import CLIUtils

fit = Fit.from_data_file(file_path=sys.argv[0:2], skip_nominal=True, fit_model="IVI")
CLIUtils.print_manager_options(solver=fit)
CLIUtils.print_solver_options(solver=fit)
CLIUtils.print_basic_statistics(solver=fit)

fit.execute()