from abc import ABC, abstractmethod

from lcall.DLInstance import DLInstance
from lcall.DLPropertyChain import DLPropertyChain
from lcall.callFormula import CallFormula
from owlready2 import Thing


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
        pass
        
    def log_call_error(self, message: str, skipMessage: str):
        pass

    def build_param_list(self, params: Thing) -> (list[DLPropertyChain] | None):
        pass

    @abstractmethod
    def instances(self) -> list[DLInstance]:
        """
        Gets instances of the ontology

        :return: list of instances of the ontology
        """
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
    def calls_for_instance(self, instance: DLInstance) -> list[CallFormula]:
        """
        Gets call formulas where the instance is in its domain

        :param instance: instance to check
        :return: call objects of the ontology for the given instance
        """
        pass

    @abstractmethod
    def reason(self):
        pass
