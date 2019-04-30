from enum import Enum
from model import Model
from typing import Sequence


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

    def set(self, **kwargs):
        pass

    def set_search_direction(self, direction: SearchDirection) -> None:
        self._ref.setSearchDirection(direction.value)

    def set_search_type(self, type_: SearchType) -> None:
        self._ref.setSearchType(type_.value)

    def get_model_by_search_dir(self, direction: SearchDirection) -> Model:
        if direction is SearchDirection.UP:
            return Model(ref=self._ref.getTopRefModel())

        return Model(ref=self._ref.getBottomRefModel())

    def has_test_data(self) -> bool:
        return self._ref.hasTestData()

    def search_one_level(self) -> Sequence[Model]:
        model_ref_list = self._ref.searchOneLevel()

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

    def print_options(self, print_html: bool, skip_nominal: bool) -> None:
        self._ref.printOptions(print_html, skip_nominal)

    # TODO: remove and replace with the underlying functionality in the future
    def print_basic_statistics(self) -> None:
        self._ref.printBasicStatistics()

    # TODO: remove and replace with the underlying functionality in the future
    def print_fit_report(self) -> None:
        self._ref.printFitReport()

