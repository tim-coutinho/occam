from wrappers.vbm_manager import VBMManager
from wrappers.manager import SearchDirection, SearchFilter, SearchType
from wrappers.model import ModelType
from typing import Optional, Sequence
import sys

class Search:

    def __init__(self, manager, search_dir, ):
        self._manger = manager
        self.search_dir = search_dir
        self._search_filter = search_filter


    def execute(self):
        #If manager type is SB
        if self._manager.is_directed():
            if self.search_dir == SearchDirection.DOWN:
                if self._search_filter == SearchFilter.DISJOINT:
                    pass
                elif self._search_filter == SearchFilter.CHAIN:
                    print(
                        'ERROR: Directed Down Chain Search not yet implemented.'
                    )
                    raise sys.exit()
        else:
            if self.search_dir == "up":
                pass
            else:
                if self._search_filter == SearchFilter.DISJOINT:
                    pass
                elif self._search_filter == SearchFilter.CHAIN:
                    print(
                        'ERROR: Neutral Down Chain Search not yet implemented.'
                    )
                    raise sys.exit()
        #Shared for SB and VB
        if self._start_model == "":
            self._start_model = ModelType.DEFAULT
        if self.search_dir == SearchDirection.DEFAULT:
            self.search_dir = SearchDirection.UP
        if (
            self._search_filter == SearchFilter.CHAIN or self._start_model == ModelType.DEFAULT
        ) and self.search_dir == SearchDirection.DOWN:
            self._start_model = ModelType.printOptions
        elif (
            self._search_filter == SearchFilter.CHAIN or self._start_model == ModelType.DEFAULT
        ) and self.search_dir == SearchDirection.UP:
            self._start_model = ModelType.BOTTOM
        if self._start_model == ModelType.TOP:
            start = self._manager.get_top_ref_model()
        elif self._start_model == ModelType.BOTTOM:
            start = self._manager.get_bottom_ref_model()
        else:
            start = self._manager.make_model(self._start_model, True)
        self.set_ref_model(self._ref_model)
        #If manager type is VB
        self._manager.use_inverse_notation(self._use_inverse_notation)
        self._manager.values_are_functions(self._values_are_functions)
        self._manager.set_alpha_threshold(self._alpha_threshold)
        #Shared for SB and VB
        if self.search_dir == SearchDirection.DOWN:
            self._manager.set_search_direction(SearchDirection.DOWN)
        else:
            self._manager.set_search_direction(SearchDirection.UP)
        if print_options:
            self.print_options(1)
        self._manager.print_basic_statistics()
        self._manager.compute_l2_statistics(start)
        self._manager.compute_dependent_statistics(start)
        #If manager type is VB
        if self._bp_statistics:
            self._manager.compute_bp_statistics(start)
        #Shared for SB and VB
        if self._percent_correct and self._manager.is_directed():
            self._manager.compute_percent_correct(start)
        if self._incremental_alpha:
            self._manager.compute_incremental_alpha(start)
        start.level = 0
        self._report.add_model(start)
        self._next_id = 1
        start.set_id(self._next_id)
        start.set_progenitor(start)
        old_models = [start]
        try:
            self._manager.set_search_type(self.search_type())
        except Exception:
            print(f"ERROR: UNDEFINED SEARCH TYPE {self.search_type()}")
            return
        if self._HTMLFormat:
            print('<pre>')
        print("Searching levels:")
        start_time = time.time()
        last_time = start_time
        for i in range(1, self._search_levels + 1):
            if self._manager.get_mem_usage() > max_memory_to_use:
                print("Memory limit exceeded: stopping search")
                break
            print(i, ':', end=' ')  # progress indicator
            new_models = self.process_level(
                i, old_models, i != self._search_levels
            )
            current_time = time.time()
            print(
                f'{current_time - last_time:.1f} seconds, {current_time - start_time:.1f} total'
            )
            #If manager type is VB
            sys.stdout.flush()
            #Shared for VB and SB
            last_time = current_time
            for model in new_models:
                # Make sure all statistics are calculated. This won't do anything if we did it already.
                if not self._no_ipf:
                    self._manager.compute_l2_statistics(model)
                    self._manager.compute_dependent_statistics(model)
                if self._bp_statistics:
                    self._manager.compute_bp_statistics(model)
                if self._percent_correct:
                    self._manager.compute_percent_correct(model)
                if self._incremental_alpha:
                    self._manager.compute_incremental_alpha(model)
                self._next_id += 1
                model.set_id(self._next_id)
                #If manager type is SB
                model.deleteFitTable()  #recover fit table memory
                #Shared for VB and SB
                self._report.add_model(model)
            old_models = new_models
            # if the list is empty, stop. Also, only do one step for chain search
            if self._search_filter == SearchFilter.CHAIN or len(old_models) == 0:
                break
        if self._HTMLFormat:
            print('</pre><br>')
        else:
            print()
