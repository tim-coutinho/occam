from fit import Fit


class CLIUtils:
    @classmethod
    def print_basic_statistics(cls, solver: Fit) -> None:
        manager = solver.manager
        state_space_size = manager.compute_df(manager.get_top_ref_model()) + 1
        top_h = manager.compute_h(manager.get_top_ref_model())
        var_names = [var.abbrev for var in manager.variable_list]

        print(f"State Space Size, {state_space_size}")
        print(f"Sample Size, {manager.sample_size}")
        print(f"H(data), {top_h}")
        print(f"Variables in use ({len(var_names)}), {','.join(var_names)}")

    @classmethod
    def print_solver_options(cls, solver: Fit) -> None:
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

