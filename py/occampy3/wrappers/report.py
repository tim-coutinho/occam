from enum import Enum
from model import Model
from relation import Relation
from variable_list import VariableList
from table import Table
from typing import Optional


class SeparatorType(Enum):
    TAB = 1
    COMMA = 2
    SPACE = 3
    HTML = 4


class SortDirection(Enum):
    ASCENDING = "ascending"
    DESCENDING = "descending"


class Report:
    """
    Wrapper class for Report
    """

    def __init__(self, ref):
        """
        :param: ref: the reference to the Report object returned from the CPP engine
        """
        self._ref = ref  # type Report_cpp

    @property
    def variable_list(self) -> VariableList:
        return VariableList(self._ref.variableList())

    @property
    def dv_name(self) -> str:
        return self._ref.dvName()

    def set_separator(self, separator: SeparatorType) -> None:
        self._ref.setSeparator(separator.value)

    def add_model(self, model: Model) -> None:
        self._ref.addModel(model.ref)

    def set_default_fit_model(self, model: Model) -> None:
        self._ref.setDefaultFitModel(model.ref)

    def print_conditional_dv(self, model: Model, calc_expected_dv: bool, classifier_target: str) -> None:
        self._ref.printConditional_DV(model.ref, calc_expected_dv, classifier_target)

    def print_residuals(self, model: Model, skip_trained_model_table: bool, skip_ivi_tables: bool) -> None:
        self._ref.printResiduals(model.ref, skip_trained_model_table, skip_ivi_tables)

    def print_table(self, relation: Optional[Relation], fit_table: Optional[Table], input_table: Table,
                    indep_table: Table, adjust_constant: float, sample_size: float,
                    print_lift: bool, print_calc: bool) -> None:

        rel = relation.ref if relation is not None else None
        fit = fit_table.ref if fit_table is not None else None

        self._ref.printTable(rel, fit, input_table.ref, indep_table.ref, adjust_constant, sample_size,
                             print_lift, print_calc)

    def set_attributes(self, attributes: str) -> None:
        self._ref.setAttributes(attributes)

    def sort(self, sort_name: str, sort_direction: SortDirection) -> None:
        self._ref.sort(sort_name, sort_direction.value)

    def write_report(self, stream: str) -> None:
        self._ref.writeReport(stream)

    def print_report(self) -> None:
        self._ref.printReport()

    def print_dyad_summary(self, model: Model) -> None:
        self._ref.printDyadSummary(model.ref)