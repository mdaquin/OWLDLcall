from abc import ABC, abstractmethod

from lcall.DLInstance import DLInstance
from lcall.DLPropertyChain import DLPropertyChain
from lcall.callFormula import CallFormula
from lcall.DLObjectProperty import DLObjectProperty
from lcall.assertion import Assertion
from lcall.DLClass import DLClass
from lcall.resultList import ResultList
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

    def add_assertions(self, results: tuple, object_prop: DLObjectProperty, _range: DLClass, res_list: ResultList, 
                       instance: DLInstance, assertions: list[Assertion]) -> list[DLInstance]:
        """
        Add assertions from object property call formulas. For example, with the `instance = a`, the `object property = r`,
        the `range = X` and the `results = (3, 'abc', False)`, the function will create a new instance `x1` such that
        `X(x1)` and if we have, for example, `(p, int, 0) in res_list` then the assertion `p(x1, 3 = results[0])` is added.
        
        :param results: The result of the function, usually a tuple of values
        :param object_prop: the object property linked to one of the assertion to add
        :param _range: the class of the new instance to create
        :param res_list: The structure showing what assertions to add
        :param instance: the instance linked to one of the assertion
        :param assertions: the list of assertions ot complete
        :return: the list of new instances created
        """
        pass
