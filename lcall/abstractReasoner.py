import typing
from abc import ABC, abstractmethod

from lcall.DLClass import DLClass
from lcall.DLInstance import DLInstance
from lcall.DLPropertyChain import DLPropertyChain
from lcall.callFormula import CallFormula
from lcall.propertyAssertion import PropertyAssertion


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

    @abstractmethod
    def instances(self) -> list[DLInstance]:
        """
        Gets instances of the ontology

        :return: list of instances of the ontology
        """
        pass

    @abstractmethod
    def _is_instance_of(self, instance: DLInstance, class_expression: DLClass) -> bool:
        """
        Checks if the given instance is in the given concept

        :param instance: instance to check
        :param class_expression: class expression to check
        :return: true if the instance is in the class, false otherwise
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
    def is_asserted(self, assertion: PropertyAssertion) -> bool:
        """
        Checks if the given assertion is already true in the ontology

        :param assertion: assertion to test
        :return: true if the assertion is already in the ontology, false otherwise
        """
        pass

    @abstractmethod
    def add_assertions(self, assertions: typing.Iterable[PropertyAssertion]):
        """
        Add assertions to the ontology

        :param assertions: assertions to add
        """
        pass
