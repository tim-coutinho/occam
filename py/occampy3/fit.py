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

        self.manager = manager
        self.skip_nominal = skip_nominal
        self._search_dir = search_dir
        self._start_model_name = start_model_name
        self._fit_model_names = fit_model_names
        self._report = self.manager.get_report()
        self._skip_trained_model_table = True
        self._skip_ivi_tables = True

        if ref_model is None:
            self._ref_model = ModelType.TOP if self._search_dir is SearchDirection.DOWN else ModelType.BOTTOM

        # TODO: Remove/replace with underlining functionality
        self._HTMLFormat = False
        self.fit_classifier_target = ""
        self._search_width = 3
        self._search_levels = 7
        self._sort_name = "ddf"
        self._search_sort_dir = SearchDirection.DOWN
        self._report_sort_name = ""
        self._sort_dir = SortDirection.ASCENDING
        self._search_filter = SearchFilter.LOOPLESS
        self.generate_graph = False
        self.generate_gephi = False
        self.layout_style = None
        self.graph_width = 500
        self.graph_height = 500
        self.graph_font_size = 12
        self.graph_node_size = 36
        self.hide_isolated = True
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
        for model_name in self._fit_model_names:
            self._check_model_name(model_name)
            model = self.manager.make_model(model_name=model_name, make_project=True)

            self.manager.compute_l2_statistics(model)
            self.manager.compute_dfs_statistics(model)
            self.manager.compute_dependent_statistics(model)

            # TODO: Remove/replace with underlining functionality
            self.manager.print_fit_report(model)

            self.manager.make_fit_table(model)

            # TODO: Remove/replace with underlining functionality
            self._report.add_model(model)
            self._report.print_residuals(model=model,
                                         skip_trained_model_table=self._skip_trained_model_table,
                                         skip_ivi_tables=self._skip_ivi_tables
                                         )

            if self._default_fit_model != "":
                try:
                    default_model = self.manager.make_model(model_name=self._default_fit_model,
                                                            make_project=True
                                                            )
                except Exception:
                    print(f"\nERROR: Unable to create model {self._default_fit_model}")
                    sys.exit(0)
                self._report.set_default_fit_model(default_model)
            self._report.print_conditional_dv(model=model,
                                              calc_expected_dv=self._calc_expected_dv,
                                              classifier_target=self.fit_classifier_target
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
            if (s == "IV" if self.manager.is_directed() else s == "IVI")
            else self.split_caps(s)
            for s in comps
        ]
        return model

    # TODO: Cleanup, replace all prints with Exceptions
    def _check_model_name(self, model_name):
        varlist = [v.abbrev for v in self.manager.variable_list]
        model = self._split_model_name(model_name)
        is_directed = self.manager.is_directed()
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
                err_msg = f"ERROR: Not all declared variables are present in the model, '{model_name}'."

                if saw_maybe_wrong_iv:
                    err_msg += f"\n_did you mean '{'IV' if is_directed else 'IVI'}' instead of '{'IVI' if is_directed else 'IV'}"
                else:
                    err_msg += f"\n Did you forget the {'IV' if is_directed else 'IVI'} component?"

                err_msg += "\n Not in model: "
                err_msg += ", ".join([f"'{i}'" for i in varset.difference(modset)])

                raise Exception(err_msg)

        # all variables in model are in varlist
        if not modset.issubset(varset):
            err_msg = f"ERROR: Not all variables in the model '{model_name}' are declared in the variable list."

            diffset = modset.difference(varset)
            if saw_maybe_wrong_iv or diffset == {"I", "V"}:
                err_msg += f"\n_did you mean '{'IV' if is_directed else 'IVI'}' instead of '{'IVI' if is_directed else 'IV'}'?"

            else:
                err_msg += "\n Not declared: "
                err_msg += ", ".join([f"'{i}'" for i in diffset])

            raise Exception(err_msg)

        # dv must be in all components (except IV) if directed
        if is_directed:
            dv = self.manager.dv_name
            for rel in model:
                if not (rel == ["IVI"] or rel == ["IV"]) and dv not in rel:
                    if self._HTMLFormat:
                        print("<br>")
                    raise Exception(
                        f"\nERROR: In the model '{model_name}', model component '{''.join(rel)}'"
                        f"is missing the DV, '{dv}'."
                    )

    def print_graph(self, model_name, only):
        if only and not self.generate_gephi:
            self.generate_graph = True
        if (self.generate_graph or self.generate_gephi) and (
                self.hide_isolated and (model_name == "IVI" or model_name == "IV")
        ):
            msg = "Note: no "
            if self.generate_graph:
                msg += "hypergraph image "
            if self.generate_graph and self.generate_gephi:
                msg += "or "
            if self.generate_gephi:
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

    def print_fit_report(self, model):
        line_sep = "-------------------------------------------------------------------------\n"
        header = ""
        beginLine = "    "
        separator = ","
        endLine = "\n"
        footer = "\n"

        directed = self.isDirected()
        print(header)
        print(beginLine, "Model", separator, model.getPrintName())

        if directed:
            print(" (Directed System)", endLine)
        else:
            print(" (Neutral System)", endLine)

        for i in range(0, model.getRelationCount()):
            print(beginLine)
            rel = model.getRelation(i)

            if directed:
                if rel.isIndependentOnly():
                    print("IV Component:")
                else:
                    print("Model Component: ")
                print(separator)

            for j in range(0, rel.getVariableCount()):
                varname = getVariableList().getVariable(rel.getVariable(j))
                if j > 0:
                    print("; ")
                print(varname)

            print(separator)
            print(rel.getPrintName())
            print(endLine)

        print(beginLine + "Degrees of Freedom (DF):" + separator + model.get("df") + endLine)
        if model.get("loops") > 0:
            valueStr = "YES"
        else:
            valueStr = "NO"
        print(beginLine + "Loops:" + separator + valueStr + endLine)
        print(beginLine + "Entropy(H):" + separator + model.get("h") + endLine)
        print(beginLine + "Information captured (%):" + separator + (model.get("information") *100) + endLine)
        print(beginLine + "Transmission (T):" + separator + model.get("t") + endLine)
        print(footer)

        attribute_lr = self.manager.getConst("ATTRIBUTE_LR")
        attribute_alpha = self.manager.getConst("ATTRIBUTE_ALPHA")
        attribute_p2 = self.manager.getConst("ATTRIBUTE_P2")
        attribute_p2_alpha = self.manager.getConst("ATTRIBUTE_P2_ALPHA")
        attribute_ddf = self.manager.getConst("ATTRIBUTE_DDF")

        topFields1 = ["Log-Likelihood (LR)", attribute_lr, attribute_alpha, "Pearson X2", attribute_p2, attribute_p2_alpha, "Delta DF (dDf)", attribute_ddf, ""]
        bottomFields1 = ["Log-Likelihood (LR)", attribute_lr, attribute_alpha, "Pearson X2", attribute_p2, attribute_p2_alpha, "Delta DF (dDF)", attribute_ddf, ""]

        sets_in_print(model, "top")
        print_ref_table(model, "TOP", topFields1, 3)

        sets_in_print(model, "bottom")
        print_ref_table(model, "BOTTOM", bottomFields1, 3)

        print(line_sep)

    def sets_in_print(self, model, refmodel):
        attribute_alg_h = self.manager.getConst("ATTRIBUTE_ALG_H")
        attribute_h = self.manager.getConst("ATTRIBUTE_H")

        h1 = model.get(attribute_alg_h)
        h2 = model.get(attribute_h)

        model.resetAttributeList()
        model.tp_setattro(attribute_alg_h, h1)
        model.tp_setattro(attribute_h, h2)

        self.manager.set_ref_model(refmodel)
        self.manager.compute_information_statistics(model)
        self.manager.compute_dependent_statistics(model)
        self.manager.compute_l2_statistics(model)
        self.manager.compute_pearson_statistics(model)

    def print_ref_table(self, model, ref, strings, rows):
        line_sep = "-------------------------------------------------------------------------\n"
        header = ""
        beginLine = "    "
        separator = ","
        endLine = "\n"
        footer = "\n"
        headerSep = "";
        cols = 3

        print(line_sep)
        print(header)
        print("\n", beginLine, "REFERENCE = ", ref, endLine)
        print(beginLine, separator, "Value", separator)
        print("Prob. (Alpha)", endLine)
        print(headerSep)

        for row in range(0, rows):
            rowlabel = row *colspan
            print(beginLine, strings[rowLabel])

            for col in range(1, cols):
                value = model.get(strings[rowlabel + col])
                if value >= 0:
                    print(separator, value)
                else:
                    print(separator)

            print(endLine)

        print(footer)
