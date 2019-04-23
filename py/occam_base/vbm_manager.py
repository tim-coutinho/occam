from occam import VBMManager as VBMManager_cpp
from variable_list import VariableList


class VBMManager:
    """
    Wrapper class for VBMManager
    """

    def __init__(self, ref=None):
        """
        :param: ref: the reference to the VBMManager object returned from the CPP engine
        """
        # Create new reference if one not given
        self._ref = ref or VBMManager_cpp()
        self._report = self._ref.Report()
        self._model = None

    @property
    def report(self):
        return self._report

    @property
    def variable_list(self):
        return VariableList(self._ref.getVariableList())

    @property
    def search_type(self):
        pass

    @search_type.setter
    def search_type(self, search_type):
        self._ref.setSearchType(search_type)

    def get_model(self, type_='default', make_project=1):
        if type_ == 'top':
            model = self._ref.getTopRefModel()
        elif type_ == 'bottom':
            model = self._ref.getBottomRefModel()
        else:
            model = self._ref.makeModel(type_, make_project)
        self._model = model
        return model

    def set(self, **kwargs):
        for k in kwargs:
            self.__dict__[k] = kwargs[k]
