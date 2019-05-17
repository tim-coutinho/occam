from wrappers.vbm_manager import VBMManager
from wrappers.sbm_manager import SBMManager
from wrappers.manager import SearchDirection, SearchFilter, SearchType
from wrappers.model import Model, ModelType
from typing import Optional, Sequence
import sys
import heapq
import time

class Search:

    def __init__(self, opt: str):
        if opt == "VB":
            self._manger = VBManager()
            self._manager_type = "VB"
        else:
            self._manger = SBMManager()
            self._manger_type = "SB"
        self.search_dir = SearchDirection.DOWN
        self._search_filter = SearchFilter.LOOPLESS
        self.report = self._manager.report
        self._start_model = ModelType.DEFUALT
        self._ref_model = ModelType.DEFAULT
        self._use_inverse_notation = False
        self._values_are_functions = False
        self._alpha_threshold = 0.05
        self._bp_statistics = 0
        self._percent_correct = 0
        self._next_id = 0
        self._hide_intermediate_output = False
        self._total_gen = 0
        self._total_kept = 0
        self._search_width = 3


    def execute(self):
        #If manager type is SB
        if self._manger_type == "SB"
            if self._manager.is_directed():
                if self.search_dir == SearchDirection.DOWN:
                    if self._search_filter == SearchFilter.DISJOINT:
                        pass
                    elif self._search_filter == SearchFilter.CHAIN:
                        print('ERROR: Directed Down Chain Search not yet implemented.')
                        raise sys.exit()
            else:
                if self.search_dir == SearchDirection.UP:
                    pass
                else:
                    if self._search_filter == SearchFilter.DISJOINT:
                        pass
                    elif self._search_filter == SearchFilter.CHAIN:
                        print('ERROR: Neutral Down Chain Search not yet implemented.')
                        raise sys.exit()
        #Shared for SB and VB
        if self._start_model == "":
            self._start_model = ModelType.DEFAULT
        if self.search_dir == SearchDirection.DEFAULT:
            self.search_dir = SearchDirection.UP

        if (
            self._search_filter == SearchFilter.CHAIN or self._start_model == ModelType.DEFAULT
        ) and self.search_dir == SearchDirection.DOWN:
            self._start_model = ModelType.TOP
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
        self._manager.set_ref_model(self._ref_model)
        #If manager type is VB
        if self._manager_type == "VB"
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
        if self._manager_type == "VB"
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
            if self._manger_type == "VB"
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
                if self._manger_type == "SB"
                    model.deleteFitTable()  #recover fit table memory
                #Shared for VB and SB
                self._report.add_model(model)
            old_models = new_models
            # if the list is empty, stop. Also, only do one step for chain search
            if self._search_filter == SearchFilter.CHAIN or len(old_models) == 0:
                break
            print()

    def process_level(self,
                      level: int,
                      old_models: List[Model],
                      clear_cache_flag: bool) -> List[Model]:
        # start a new heap
        new_models_heap = []
        full_count = 0
        for model in old_models:
            full_count += self.process_model(level, new_models_heap, model)
        # if search_width < heapsize, pop off search_width and add to best_models
        best_models = []
        while len(new_models_heap) > 0:
            # make sure that we're adding unique models to the list (mostly for state-based)
            key, candidate = heapq.heappop(new_models_heap)
            # if len(best_models) < self._search_width:  # or key[0] == last_key[0]:      # comparing keys allows us to select more than <width> models,
            if len(best_models) < self._search_width and not any(
                {n == candidate for n in best_models}
            ):  # in the case of ties
                best_models.append(candidate)
            else:
                break
        trunc_count = len(best_models)
        self._total_gen = full_count + self._total_gen
        self._total_kept = trunc_count + self._total_kept
        mem_used = self._manager.mem_usage
        if not self._hide_intermediate_output:
            print(
                f'{full_count} new models, {trunc_count} kept; '
                f'{self._total_gen + 1} total models, '
                f'{self._total_kept + 1} total kept; '
                f'{mem_used / 1024} kb memory used; ',
                end=' ',
            )
        sys.stdout.flush()
        if clear_cache_flag:
            for item in new_models_heap:
                self._manager.delete_model_from_cache(item[1])
        return best_models

    def print_option(self, label: str, value: str) -> None:
            print(f"{label},{value}")

    def print_options(self, r_type: int) -> None:
        self._manager.print_options(self._HTMLFormat, self._skip_nominal)
        self.print_option("Input data file", self._data_file)

        if self._fit_classifier_target != "":
            self.print_option(
                "Default ('negative') state for confusion matrices",
                self._fit_classifier_target,
            )

        if r_type == 1:
            self.print_option("Starting model", self.start_model)
            self.print_option("Search direction", self.search_dir)
            self.print_option("Ref model", self._ref_model)
            self.print_option("Models to consider", self._search_filter)
            self.print_option("Search width", self._search_width)
            self.print_option("Search levels", self._search_levels)
            self.print_option("Search sort by", self.sort_name)
            self.print_option("Search preference", self._search_sort_dir)
            self.print_option("Report sort by", self._report_sort_name)
            self.print_option("Report preference", self._sort_dir.value)

        if r_type == 0:
            self.print_option(
                "Generate hypergraph images",
                "Y" if self._generate_graph else "N",
            )
            self.print_option(
                "Generate Gephi files", "Y" if self._generate_gephi else "N"
            )

        if self._generate_graph:
            self.print_option(
                "Hypergraph layout style", str(self._layout_style)
            )
            self.print_option("Hypergraph image width", str(self._graph_width))
            self.print_option(
                "Hypergraph image height", str(self._graph_height)
            )
            self.print_option(
                "Hypergraph font size", str(self._graph_font_size)
            )
            self.print_option(
                "Hypergraph node size", str(self._graph_node_size)
            )

        if self._generate_gephi or self._generate_graph:
            self.print_option(
                f"Hide {'IV' if self.is_directed else 'IVI'} components in hypergraph",
                "Y" if self._hide_isolated else "N",
            )
        sys.stdout.flush()
