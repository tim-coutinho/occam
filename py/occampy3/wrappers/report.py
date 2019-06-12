from enum import Enum
from model import Model
from variable_list import VariableList


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

    def set_attributes(self, attributes: str) -> None:
        self._ref.setAttributes(attributes)

    def sort(self, sort_name: str, sort_direction: SortDirection) -> None:
        self._ref.sort(sort_name, sort_direction.value)

    def write_report(self, stream: str) -> None:
        self._ref.writeReport(stream)

    def print_report(self) -> None:
        self._ref.printReport()

    def get_separator(self) -> int:
        self._ref.getSeparator()

    # Translation of the original header function in ReportCommon.cpp
    def header(self, rel, print_lift: bool, print_calc: bool, print_start: bool) -> None:
        var_list = manager.getVariableList()
        var_count = var_list.var_count()

        separator_value = get_separator()
        delim_types = ["\t", ",", " "]
        hdr = delim_types[separator_value]



    #   TODO: Implement if rel else from original header function in ReportCommon.cpp
    #   Will need to implement translation of getIndependentVariables for Relation




        seperator_types = ["\t", ",", "    "]
        seperator = seperator_types[separator_value]
        print("|", hdr, "0bs.Prob.", seperator, "0bs.Freq.")

        if print_calc:
            print(hdr, "|", hdr, "Calc.Prob.", hdr, "Calc.Freq.", hdr, "Residual")

        if print_lift:
            print(hdr, "|", hdr, "Ind.Prob.", hdr, "Ind.Freq.", hdr, "Lift")

        print("\n")


    def print_table_row(self, blue: bool, varlist: VariableList, var_count:int):
        # TODO: Needs to be implemented
        keystr = []


    def print_table(self, rel, fit_table, input_table, indep_table, adjust_constant: float, sample_size: float, print_lift: bool, print_calc: bool) -> None:
        if rel:
            var_list = rel.getVariableList()
        else:
            var_list = manager.getVariableList()

        var_count = var_list.var_count

        header(rel, print_lift, print_calc)

        blue = 1;
        value_total = 0.0
        ref_value_total = 0.0
        ivi_value_total = 0.0

        last_ref_key = None
        saw_undefined_lift = False

        def table_action(self, rel, value: float, ref_key, ref_value: float, ivi_value: float) -> None:
            if (ivi_value == 0 and value == 0):
                saw_undefined_lift = true

            value_total += value
            ref_value_total += ref_value_total
            ivi_value += ivi_value_total

            print_table_row()

            blue = not blue
            last_ref_key = ref_key


        # TODO: implement python version of table_iteration from table.h

        # TODO: implement table_totals inner method from ReportCommon.cpp
        # table_totals(value_total, ref_value_total, ivi_value_total, sample_size)

        header(rel, print_lift, print_calc, False)

        # TODO: get the PRINT_MIN
        print_min = 0.00000001
        if ((print_calc and (1 - value_total) > print_min)
        or (print_lift and (1 - ivi_value_total > print_min))
        or saw_undefined_lift):
            print("Note: \n")

        if(print_calc and (1 - value_total) > print_min):
            print("The calculated probabilities sum to less than 1\n")
            print("(and the total residual is less than 0)\n")
            print("because the calculated distribution has probability\n")
            print("distributed over states that were not observed in the data. \n")

        if(print_lift and (1- ivi_value_total > print_min)):
            print("The independence probabilities sum to less than 1\n")
            print(" because the independence distribution has probability\n")
            print(" distributed over states that were not observed in the data. \n")

        if(saw_undefined_lift):
            print("One or more states has an undefined (\"-nan\") lift value,\n")
            print(" because the calculated and independence probabilities are both 0,\n")
            print(" possibly because the state was never seen in the training data. \n")

        if((print_calc and (1 - value_total) > print_min)
        or (print_lift and (1 - ivi_value_total > print_min))
        or saw_undefined_lift):
            print("\n\n")
