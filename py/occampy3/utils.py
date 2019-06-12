from wrappers.table import Table
from wrappers.model import Model
from wrappers.report import Report
from wrappers.vbm_manager import VBMManager
from wrappers.relation import Relation
from typing import Optional


class CLIUtils:
    @classmethod
    def print_basic_statistics(cls, solver) -> None:
        manager = solver.manager
        state_space_size = manager.compute_df(manager.get_top_ref_model()) + 1
        top_h = manager.compute_h(manager.get_top_ref_model())
        var_names = [var.abbrev for var in manager.variable_list]

        print(f"State Space Size, {state_space_size}")
        print(f"Sample Size, {manager.sample_size}")
        print(f"H(data), {top_h}")
        print(f"Variables in use ({len(var_names)}), {','.join(var_names)}")

    @classmethod
    def print_manager_options(cls, solver) -> None:
        print("Option settings:")

        if solver.skip_nominal:
            print("(Omitting variable definitions.)")

        for option in solver.manager.all_options():
            if solver.skip_nominal and option.name == 'nominal':
                continue

            print(f"{option.name}: {option.value}")

    @classmethod
    def print_solver_options(cls, solver) -> None:
        if solver.fit_classifier_target != "":
            print(f"Default ('negative') state for confusion matrices {solver.fit_classifier_target}")

        print(f"Generate hypergraph images {'Y' if solver.generate_graph else 'N'}")
        print(f"Generate Gephi files {'Y' if solver.generate_gephi else 'N'}")

        if solver.generate_graph:
            print(f"Hypergraph layout style {str(solver.layout_style)}")
            print(f"Hypergraph image width {str(solver.graph_width)}")
            print(f"Hypergraph image height {str(solver.graph_height)}")
            print(f"Hypergraph font size {str(solver.graph_font_size)}")
            print(f"Hypergraph node size {str(solver.graph_node_size)}")

        if solver.generate_gephi or solver.generate_graph:
            components = 'IV' if solver.manager.is_directed() else 'IVI'
            hide_isolated = 'Y' if solver.hide_isolated else 'N'

            print(f"Hide {components} components in hypergraph {hide_isolated}")

    @classmethod
    def _print_test_data(cls, report: Report, manager: VBMManager, relation: Optional[Relation],
                         fit_table: Optional[Table], indep_table: Table, adjust_constant: float,
                         key_size: int, print_calc: bool, print_lift: bool):

        test_data = manager.test_data
        sample_size = manager.sample_size

        if test_data is None or sample_size <= 0:
            return

        print("Test Data")
        if relation is None:
            test_table = Table.new_table(key_size=key_size, tuple_count=test_data.tuple_count)
        else:
            test_table = test_data
            manager.make_projection(input_data=test_data, input_table=test_table, relation=relation)

        report.print_table(relation=relation, fit_table=fit_table, input_table=test_table,
                           indep_table=indep_table, adjust_constant=adjust_constant, sample_size=sample_size,
                           print_lift=print_lift, print_calc=print_calc)

    @classmethod
    def _print_rel(cls, report: Report, manager: VBMManager, relation: Relation,
                   adjust_constant: float, print_lift: bool):
        sample_size = manager.sample_size
        input_data = manager.input_data
        key_size = input_data.key_size
        input_table = Table.new_table(key_size=key_size, tuple_count=input_data.tuple_count)

        manager.make_projection(input_data=input_data, input_table=input_table, relation=relation)

        if print_lift:
            indep_table = manager.projected_fit(relation=relation, model=manager.get_top_ref_model())
        else:
            indep_table = None

        report.print_table(relation=relation, fit_table=None, input_table=input_table,
                           indep_table=indep_table, adjust_constant=adjust_constant, sample_size=sample_size,
                           print_lift=print_lift, print_calc=False)

        cls._print_test_data(manager=manager, report=report, relation=relation, fit_table=None, indep_table=indep_table,
                             adjust_constant=adjust_constant, key_size=key_size,
                             print_calc=False, print_lift=print_lift)

    @classmethod
    def _print_whole_table(cls, model: Model, manager: VBMManager, report: Report, adjust_constant: float) -> None:
        print(f"Observations for all states for the Model {model.print_name}")

        input_table = manager.input_data
        key_size = input_table.key_size
        fit_table = Table.new_table(key_size=key_size, tuple_count=input_table.tuple_count)

        manager.make_fit_table(model=model)

        fit_table.copy(table=manager.fit_table)
        indep_table = manager.indep_table

        print("Variable order: ")
        for variable in manager.variable_list:
            print(f"{variable.abbrev}")

        sample_size = manager.sample_size

        report.print_table(relation=None, fit_table=fit_table, input_table=input_table, indep_table=indep_table,
                           adjust_constant=adjust_constant, sample_size=sample_size, print_lift=True, print_calc=True)

        cls._print_test_data(manager=manager, report=report, relation=None, fit_table=fit_table,
                             indep_table=indep_table, adjust_constant=adjust_constant, key_size=key_size,
                             print_calc=True, print_lift=True)

    @classmethod
    def print_residuals(cls, model: Model, report: Report, skip_trained_model_table: bool, skip_ivi_tables: bool,
                        manager: VBMManager):

        if manager.is_directed():
            return

        adjust_constant = manager.function_constant + manager.negative_constant
        relation_count = model.relation_count

        true_relation_count = 0
        dyad_count = 0

        for i in range(relation_count):
            relation = model.get_relation(i)

            if relation.variable_count > 1:
                true_relation_count += 1

                if relation.variable_count == 2:
                    dyad_count += 1

        # printDyadSummary
        if dyad_count > 1:
            report.print_dyad_summary(model)

        # printSingleVariable
        if relation_count > 1 and not skip_ivi_tables:
            for i in range(relation_count):
                relation = model.get_relation(i)

                if relation.variable_count == 1:
                    print(f"\nObservations for the Relation {relation.print_name}")
                    cls._print_rel(report=report, manager=manager, relation=relation,
                                   adjust_constant=adjust_constant, print_lift=False)

        # printLift
        if relation_count > 1:
            for i in range(relation_count):
                relation = model.get_relation(i)

                if relation.variable_count > 1:
                    print(f"\nObservations for the Relation {relation.print_name}")
                    cls._print_rel(report=report, manager=manager, relation=relation,
                                   adjust_constant=adjust_constant, print_lift=True)

        # printSummary
        if true_relation_count > 1 and true_relation_count != relation_count:
            manager.print_summary(model=model, adjust_constant=adjust_constant)

        # printWholeTable
        if not skip_trained_model_table or true_relation_count == relation_count:
            cls._print_whole_table(model=model, manager=manager, report=report, adjust_constant=adjust_constant)
