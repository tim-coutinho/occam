from wrappers.vbm_manager import VBMManager
from wrappers.manager import SearchDirection
from wrappers.model import ModelType
from typing import Optional, Sequence
import re
import sys


class Fit:
    def __init__(self,
                 manager: VBMManager,
                 skip_nominal: bool = True,
                 search_dir: SearchDirection = SearchDirection.DOWN,
                 ref_model: Optional[ModelType] = None,
                 start_model_name: Optional[str] = None,
                 fit_model_names: Optional[Sequence[str]] = None
                 ):

        self._manager = manager
        self._skip_nominal = skip_nominal
        self._search_dir = search_dir
        self._start_model_name = start_model_name
        self._fit_model_names = fit_model_names
        self._report = self._manager.get_report()
        self._skip_trained_model_table = False
        self._skip_ivi_tables = True

        if ref_model is None:
            self._ref_model = ModelType.TOP if self._search_dir is SearchDirection.DOWN else ModelType.BOTTOM

        # TODO: Remove/replace with underlining functionality
        self._HTMLFormat = False

    @classmethod
    def from_data_file(cls, file_path: str, skip_nominal: bool) -> 'Fit':
        kwargs = {}

        manager = VBMManager()
        kwargs['manager'] = manager
        kwargs['skip_nominal'] = skip_nominal

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
            kwargs['fit_model_names'] = tuple(name for name in model_names)

        return Fit(**kwargs)

    def execute(self):
        # TODO: Remove/replace with underlining functionality
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

    # TODO: cleanup, possibly remove
    def split_caps(s):
        return re.findall('[A-Z][^A-Z]*', s)

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
                print(
                    f"\nERROR: Not all declared variables are present in the model, '{model_name}'."
                )
                if self._HTMLFormat:
                    print("<br>")
                if saw_maybe_wrong_iv:
                    print(
                        f"\n_did you mean '{'IV' if is_directed else 'IVI'}' instead of '{'IVI' if is_directed else 'IV'}"
                    )
                else:
                    print(
                        f"\n Did you forget the {'IV' if is_directed else 'IVI'} component?"
                    )
                if self._HTMLFormat:
                    print("<br>")
                print("\n Not in model: ")
                print(", ".join([f"'{i}'" for i in varset.difference(modset)]))
                sys.exit(1)

        # all variables in model are in varlist
        if not modset.issubset(varset):
            if self._HTMLFormat:
                print("<br>")
            print(
                f"\nERROR: Not all variables in the model '{model_name}' are declared in the variable list."
            )
            if self._HTMLFormat:
                print("<br>")
            diffset = modset.difference(varset)
            if saw_maybe_wrong_iv or diffset == {"I", "V"}:
                print(
                    f"\n_did you mean '{'IV' if is_directed else 'IVI'}' instead of '{'IVI' if is_directed else 'IV'}'?"
                )
            else:
                print("\n Not declared: ")
                print(", ".join([f"'{i}'" for i in diffset]))

            sys.exit(1)

        # dv must be in all components (except IV) if directed
        if is_directed:
            dv = self._manager.dv_name
            for rel in model:
                if not (rel == ["IVI"] or rel == ["IV"]) and dv not in rel:
                    if self._HTMLFormat:
                        print("<br>")
                    print(
                        f"\nERROR: In the model '{model_name}', model component '{''.join(rel)}'"
                        f"is missing the DV, '{dv}'."
                    )
                    sys.exit(1)
