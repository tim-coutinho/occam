from enum import Enum
from model import Model
from report import Report
from option import Option
from table import Table
from relation import Relation
from typing import Sequence, Union, Optional


class SearchDirection(Enum):
    UP = 0
    DOWN = 1


class SearchType(Enum):
    LOOPLESS_UP = 'loopless-up'
    DISJOINT_UP = 'disjoint-up'
    CHAIN_UP = 'chain-up'
    FULL_UP = 'full-up'

    LOOPLESS_DOWN = 'loopless-down'
    DISJOINT_DOWN = 'disjoint-down'
    CHAIN_DOWN = 'chain-down'
    FULL_DOWN = 'full-down'


class SBSearchType(Enum):
    LOOPLESS_UP = 'sb-loopless-up'
    DISJOINT_UP = 'sb-disjoint-up'
    CHAIN_UP = 'sb-chain-up'
    FULL_UP = 'sb-full-up'

    LOOPLESS_DOWN = 'sb-loopless-down'
    DISJOINT_DOWN = 'sb-disjoint-down'
    CHAIN_DOWN = 'sb-chain-down'
    FULL_DOWN = 'sb-full-down'


class SearchFilter(Enum):
    LOOPLESS = 'loopless'
    DISJOINT = 'disjoint'
    CHAIN = 'chain'


class Manager:
    """
    Wrapper class for Manager
    """

    def __init__(self, ref) -> None:
        """
        :param: ref: the reference to the (VBM,SBM)Manager object returned from the CPP engine
        """
        # Create new reference if one not given
        self._ref = ref
        self._model = None

    @property
    def model(self, type_='default', make_project=1):
        if type_ == 'top':
            model_ref = self._ref.getTopRefModel()
        elif type_ == 'bottom':
            model_ref = self._ref.getBottomRefModel()
        else:
            model_ref = self._ref.makeModel(type_, make_project)
        self._model = Model(model_ref)
        return self._model

    @property
    def search_type(self):
        pass

    @search_type.setter
    def search_type(self, search_type):
        self._ref.setSearchType(search_type)

    @property
    def sample_size(self) -> int:
        return int(self._ref.getSampleSz())

    @property
    def function_constant(self) -> float:
        return self._ref.getFunctionConstant()

    @property
    def negative_constant(self) -> float:
        return self._ref.getNegativeConstant()

    @property
    def input_data(self) -> Table:
        return Table.from_ref(self._ref.getInputData())

    @property
    def test_data(self) -> Optional[Table]:
        return Table.from_ref(self._ref.getTestData())

    @property
    def fit_table(self) -> Table:
        return Table.from_ref(self._ref.getFitTable())

    @property
    def indep_table(self) -> Table:
        return Table.from_ref(self._ref.getIndepTable())

    def all_options(self) -> Sequence[Option]:
        return [Option(option_ref) for option_ref in self._ref.getAllOptions()]

    def set(self, **kwargs):
        pass

    def make_projection(self, input_data: Optional[Table], input_table: Table, relation: Relation) -> bool:
        input_ = input_data.ref if input_data is not None else None

        return self._ref.makeProjection(input_, input_table.ref, relation.ref)

    def projected_fit(self, relation: Relation, model: Model) -> Table:
        return Table.from_ref(self._ref.projectedFit(relation.ref, model.ref))

    def get_report(self) -> Report:
        return Report(self._ref.Report())

    def init_from_command_line(self, args: Sequence[str]) -> None:
        self._ref.initFromCommandLine(args)

    def get_option(self, option_name: str) -> str:
        return self._ref.getOption(option_name)

    def get_option_list(self, option_name: str) -> Sequence[str]:
        return self._ref.getOptionList(option_name)

    def is_directed(self) -> bool:
        return self._ref.isDirected()

    def compute_bp_statistics(self, model: Model) -> None:
        self._ref.computeBPStatistics(model.ref)

    def compute_l2_statistics(self, model: Model) -> None:
        self._ref.computeL2Statistics(model.ref)

    def compute_dfs_statistics(self, model: Model) -> None:
        self._ref.computeDFStatistics(model.ref)

    def compute_dependent_statistics(self, model: Model) -> None:
        self._ref.computeDependentStatistics(model.ref)

    def get_top_ref_model(self) -> Model:
        return Model(self._ref.getTopRefModel())

    def get_bottom_ref_model(self) -> Model:
        return Model(self._ref.getBottomRefModel())

    def set_search_direction(self, direction: SearchDirection) -> None:
        self._ref.setSearchDirection(direction.value)

    def set_search_type(self, type_: Union[SearchType, SBSearchType]) -> None:
        self._ref.setSearchType(type_.value)

    def get_model_by_search_dir(self, direction: SearchDirection) -> Model:
        if direction is SearchDirection.UP:
            return self.get_top_ref_model()

        return self.get_bottom_ref_model()

    def has_test_data(self) -> bool:
        return self._ref.hasTestData()

    def search_one_level(self, model: Model) -> Sequence[Model]:
        model_ref_list = self._ref.searchOneLevel(model.ref)

        return tuple(Model(model_ref) for model_ref in model_ref_list)

    def compare_progenitors(self, model: Model, progen: Model) -> None:
        self._ref.compareProgenitors(model.ref, progen.ref)

    def get_mem_usage(self) -> int:
        return self._ref.getMemUsage()

    def delete_model_from_cache(self, model: Model) -> bool:
        return self._ref.deleteModelFromCache(model.ref)

    def compute_percent_correct(self, model: Model) -> None:
        self._ref.computePercentCorrect(model.ref)

    def compute_incremental_alpha(self, model: Model) -> None:
        self._ref.computeIncrementalAlpha(model.ref)

    def compute_df(self, model: Model) -> float:
        return self._ref.computeDF(model.ref)

    def compute_h(self, model: Model) -> float:
        return self._ref.computeH(model.ref)

    def make_fit_table(self, model: Model) -> None:
        self._ref.makeFitTable(model.ref)

    def print_options(self, print_html: bool, skip_nominal: bool) -> None:
        self._ref.printOptions(print_html, skip_nominal)

    def print_summary(self, model: Model, adjust_constant: float) -> None:
        self._ref.printSummary(model.ref, adjust_constant)

    # TODO: remove and replace with the underlying functionality in the future
    def print_basic_statistics(self) -> None:
        self._ref.printBasicStatistics()

    # TODO: remove and replace with the underlying functionality in the future
    def print_fit_report(self, model: Model) -> None:
        self._ref.printFitReport(model.ref)
