from abc import ABC, abstractmethod

from lcall.DLInstance import DLInstance
from lcall.DLPropertyChain import DLPropertyChain
from lcall.callFormula import CallFormula
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

    def add_assertions(self, result, param, param1, param2, individual, new_assertions):
        pass
