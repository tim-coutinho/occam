import sys
sys.path.insert(0, "./wrappers")

from wrappers.report import SortDirection
from wrappers.vbm_manager import VBMManager
from wrappers.manager import SearchDirection, SearchFilter
from wrappers.model import ModelType
from typing import Optional, Sequence
import re


class Fit:
    def __init__(self,
                 manager: VBMManager,
                 skip_nominal: Optional[bool] = True,
                 ref_model: Optional[ModelType] = None,
                 search_dir: Optional[SearchDirection] = SearchDirection.DOWN,
                 start_model_name: Optional[str] = None,
                 fit_model_names: Optional[Sequence[str]] = None
                 ):

        self._manager = manager
        self._skip_nominal = skip_nominal
        self._search_dir = search_dir
        self._start_model_name = start_model_name
        self._fit_model_names = fit_model_names
        self._report = self._manager.get_report()
        self._skip_trained_model_table = True
        self._skip_ivi_tables = True

        if ref_model is None:
            self._ref_model = ModelType.TOP if self._search_dir is SearchDirection.DOWN else ModelType.BOTTOM

        # TODO: Remove/replace with underlining functionality
        self._HTMLFormat = False
        self._fit_classifier_target = ""
        self._search_width = 3
        self._search_levels = 7
        self._sort_name = "ddf"
        self._search_sort_dir = SearchDirection.DOWN
        self._report_sort_name = ""
        self._sort_dir = SortDirection.ASCENDING
        self._search_filter = SearchFilter.LOOPLESS
        self._generate_graph = False
        self._generate_gephi = False
        self._layout_style = None
        self._graph_width = 500
        self._graph_height = 500
        self._graph_font_size = 12
        self._graph_node_size = 36
        self._hide_isolated = True
        self._default_fit_model = ""
        self._calc_expected_dv = False

    @classmethod
    def from_data_file(cls, file_path: Sequence[str], skip_nominal: bool, fit_model: str) -> 'Fit':
        kwargs = {}

        manager = VBMManager()
        kwargs['manager'] = manager
        kwargs['skip_nominal'] = skip_nominal
        kwargs['fit_model_names'] = [fit_model]

        manager.init_from_command_line(args=file_path)

        option = manager.get_option("reference-model")
        if option:
            kwargs['ref_model'] = ModelType(option)

        option = manager.get_option("search-direction")
        if option:
            kwargs['search_dir'] = SearchDirection(option)

        model_names = manager.get_option_list("short-model")
        if model_names:
            kwargs['start_model_name'] = model_names[0]
            kwargs['fit_model_names'].extend([name for name in model_names])

        return Fit(**kwargs)

    def execute(self):
        # TODO: Remove/replace with underlining functionality
        self._print_options(0)
        self._manager.print_basic_statistics()

        for model_name in self._fit_model_names:
            self._check_model_name(model_name)
            model = self._manager.make_model(model_name=model_name, make_project=True)

            self._manager.compute_l2_statistics(model)
            self._manager.compute_dfs_statistics(model)
            self._manager.compute_dependent_statistics(model)

            # TODO: Remove/replace with underlining functionality
            self._report.add_model(model)

            # TODO: Remove/replace with underlining functionality
            self._manager.print_fit_report(model)

            self._manager.make_fit_table(model)

            # TODO: Remove/replace with underlining functionality
            self._report.print_residuals(model=model,
                                         skip_trained_model_table=self._skip_trained_model_table,
                                         skip_ivi_tables=self._skip_ivi_tables
                                         )

            if self._default_fit_model != "":
                try:
                    default_model = self._manager.make_model(model_name=self._default_fit_model,
                                                             make_project=True
                                                             )
                except Exception:
                    print(f"\nERROR: Unable to create model {self._default_fit_model}")
                    sys.exit(0)
                self._report.set_default_fit_model(default_model)
            self._report.print_conditional_dv(model=model,
                                              calc_expected_dv=self._calc_expected_dv,
                                              classifier_target=self._fit_classifier_target
                                              )

            self.print_graph(model_name, True)

    # TODO: cleanup, possibly remove
    def split_caps(self, string):
        return re.findall('[A-Z][^A-Z]*', string)

    # TODO: cleanup
    def _split_model_name(self, model_name):
        comps = model_name.split(":")
        model = [
            [s]
            if (s == "IV" if self._manager.is_directed() else s == "IVI")
            else self.split_caps(s)
            for s in comps
        ]
        return model

    # TODO: Cleanup, replace all prints with Exceptions
    def _check_model_name(self, model_name):
        varlist = [v.abbrev for v in self._manager.variable_list]
        model = self._split_model_name(model_name)
        is_directed = self._manager.is_directed()
        have_ivs = False
        saw_maybe_wrong_iv = False

        # IV can be present if directed system; IVI otherwise
        if is_directed:
            if ["I", "V", "I"] in model:
                saw_maybe_wrong_iv = True
            if ["IV"] in model:
                have_ivs = True
        else:
            if ["I", "V"] in model:
                saw_maybe_wrong_iv = True
            if ["IVI"] in model:
                have_ivs = True

                # all variables in varlist are in model (possibly as IV or IVI)
        modelvars = [var for rel in model for var in rel]

        varset = set(varlist)
        modset = set(modelvars)
        if is_directed:
            modset.discard("IV")
        else:
            modset.discard("IVI")

        if not have_ivs:
            if not varset.issubset(modset):
                if self._HTMLFormat:
                    print("<br>")
                raise Exception(
                    f"\nERROR: Not all declared variables are present in the model, '{model_name}'."
                )
                if self._HTMLFormat:
                    print("<br>")
                if saw_maybe_wrong_iv:
                    raise Exception(
                        f"\n_did you mean '{'IV' if is_directed else 'IVI'}' instead of '{'IVI' if is_directed else 'IV'}"
                    )
                else:
                    raise Exception(
                        f"\n Did you forget the {'IV' if is_directed else 'IVI'} component?"
                    )
                if self._HTMLFormat:
                    print("<br>")
                raise Exception("\n Not in model: ")
                raise Exception(", ".join([f"'{i}'" for i in varset.difference(modset)]))
                sys.exit(1)

        # all variables in model are in varlist
        if not modset.issubset(varset):
            if self._HTMLFormat:
                print("<br>")
            raise Exception(
                f"\nERROR: Not all variables in the model '{model_name}' are declared in the variable list."
            )
            if self._HTMLFormat:
                print("<br>")
            diffset = modset.difference(varset)
            if saw_maybe_wrong_iv or diffset == {"I", "V"}:
                raise Exception(
                    f"\n_did you mean '{'IV' if is_directed else 'IVI'}' instead of '{'IVI' if is_directed else 'IV'}'?"
                )
            else:
                raise Exception("\n Not declared: ")
                raise Exception(", ".join([f"'{i}'" for i in diffset]))

            sys.exit(1)

        # dv must be in all components (except IV) if directed
        if is_directed:
            dv = self._manager.dv_name
            for rel in model:
                if not (rel == ["IVI"] or rel == ["IV"]) and dv not in rel:
                    if self._HTMLFormat:
                        print("<br>")
                    raise Exception(
                        f"\nERROR: In the model '{model_name}', model component '{''.join(rel)}'"
                        f"is missing the DV, '{dv}'."
                    )
                    sys.exit(1)

    def _print_option(self, label, value):
        if self._HTMLFormat:
            print(f"<tr><td>{label}</td><td>{value}</td></tr>")
        else:
            print(f"{label},{value}")

    def _print_options(self, r_type):
        if self._HTMLFormat:
            print("<br><table border=0 cellpadding=0 cellspacing=0>")
        self._manager.print_options(self._HTMLFormat, self._skip_nominal)

        if self._fit_classifier_target != "":
            self._print_option(
                "Default ('negative') state for confusion matrices",
                self._fit_classifier_target,
            )
        if r_type == 1:
            self._print_option("Starting model", self._start_model_name)
            self._print_option("Search direction", self._search_dir)
            self._print_option("Ref model", self._ref_model)
            self._print_option("Models to consider", self._search_filter.value)
            self._print_option("Search width", self._search_width)
            self._print_option("Search levels", self._search_levels)
            self._print_option("Search sort by", self._sort_name)
            self._print_option("Search preference", self._search_sort_dir)
            self._print_option("Report sort by", self._report_sort_name)
            self._print_option("Report preference", self._sort_dir.value)

        if r_type == 0:
            self._print_option(
                "Generate hypergraph images",
                "Y" if self._generate_graph else "N",
            )
            self._print_option(
                "Generate Gephi files", "Y" if self._generate_gephi else "N"
            )

        if self._generate_graph:
            self._print_option(
                "Hypergraph layout style", str(self._layout_style)
            )
            self._print_option("Hypergraph image width", str(self._graph_width))
            self._print_option(
                "Hypergraph image height", str(self._graph_height)
            )
            self._print_option(
                "Hypergraph font size", str(self._graph_font_size)
            )
            self._print_option(
                "Hypergraph node size", str(self._graph_node_size)
            )

        if self._generate_gephi or self._generate_graph:
            self._print_option(
                f"Hide {'IV' if self._manager.is_directed() else 'IVI'} components in hypergraph",
                "Y" if self._hide_isolated else "N",
            )

        if self._HTMLFormat:
            print("</table>")
        sys.stdout.flush()

    def print_graph(self, model_name, only):
        if only and not self._generate_gephi:
            self._generate_graph = True
        if (self._generate_graph or self._generate_gephi) and (
            self._hide_isolated and (model_name == "IVI" or model_name == "IV")
        ):
            msg = "Note: no "
            if self._generate_graph:
                msg += "hypergraph image "
            if self._generate_graph and self._generate_gephi:
                msg += "or "
            if self._generate_gephi:
                msg += "Gephi input "
            msg += (" was generated, since the model contains only "
                    f"{model_name} components, which were requested to be "
                    "hidden in the graph")

            if self._HTMLFormat:
                print("<br>")
            print(msg)
            if self._HTMLFormat:
                print("<br>")

        else:
            pass
            # self.maybe_print_graph_svg(model_name, True)
            # self.maybe_print_graph_gephi(model_name, True)
        print("\n")


Fit.from_data_file(file_path=sys.argv[0:2], skip_nominal=True, fit_model="IVI").execute()
