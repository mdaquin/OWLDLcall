from abc import ABC, abstractmethod
from lcall.DLInstance import DLInstance

from lcall.assertion import Assertion


class PropertyAssertion(Assertion, ABC):
    """
    An object representing a property assertion in description logics
    """

    @abstractmethod
    def get_instance(self) -> DLInstance:
        pass

    @abstractmethod
    def get_property(self):
        pass

    @abstractmethod
    def get_value(self):
        pass
