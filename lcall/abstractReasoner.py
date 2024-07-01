from abc import ABC, abstractmethod

from lcall.DLInstance import DLInstance
from lcall.DLPropertyChain import DLPropertyChain
from lcall.callFormula import CallFormula
from lcall.assertion import Assertion
from typing import Generator


class AbstractReasoner(ABC):
    """
    Reasoner interface for the Lcall controller

    The set of methods defined in this class represents the necessary parts for Lcall reasoning.
    Internal access of an ontology is left to the implementation.
    """

    @abstractmethod
    def __init__(self):
        """
        Loads ontology and performs necessary steps to get working : initial reasoner sync and call formulas fetching
        """
        self.instances: list[DLInstance] = []
        pass

    @abstractmethod
    def list_val_params(self, instance: DLInstance, params: list[DLPropertyChain]) -> list:
        """
        Gets parameter combinations for an instance

        :param instance: instance to get the parameter combinations
        :param params: list of parameters (property chains)
        :return: parameters combinations for the instance
        """
        pass

    @abstractmethod
    def calls_for_instance(self, instance: DLInstance) -> Generator[CallFormula, None, None]:
        """
        Gets call formulas where the instance is in its domain

        :param instance: instance to check
        :return: call objects of the ontology for the given instance
        """
        pass

    @abstractmethod
    def reason(self) -> bool:
        """
        Call an OWL DL reasoner (such as Hermit)
        :return: True if no inconsistencies were detected, false otherwise
        """
        pass

    def add_object_prop_assertions(self, call: CallFormula, result: tuple[str, list[tuple]], 
                                   instance: DLInstance, assertions: list[Assertion]) -> DLInstance:
        """
        The call function returns a string representing the main new instance and a list of pseudo-assertions.
        This function transforms the pseudo-assertions to assertions 
        and adds them and other assertions to the list of assertions.

        :param call: the call (for the range and subsuming property)
        :param result: a tuple of 2 elements : The name of the main instance and A list of 
        pseudo-assertions, tuples of 2 or 3 strings, for example ("inst", "prop", "value")
        :param instance: the instance from which the call was executed
        :param assertions: list of assertions to complete
        :return: the new instance
        """
        pass
