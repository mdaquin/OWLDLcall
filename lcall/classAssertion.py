from lcall.DLClass import DLClass
from lcall.assertion import Assertion
from lcall.owlRdyInstance import OwlRdyInstance
from owlready2 import Thing


class ClassAssertion(Assertion):
    """
    An object representing a class assertion in description logics
    """

    def __init__(self, concept: DLClass):
        """
        Initialization

        :param concept: the concept of the assertion
        """
        # None means the concept was not specified
        self.concept = concept if concept is not None else Thing
        # WARNING, this creates an instance
        self.instance = OwlRdyInstance(self.concept())

    def get_concept(self) -> DLClass:
        return self.concept
    
    def get_instance(self) -> OwlRdyInstance:
        return self.instance

    def __repr__(self):
        return f'{self.concept}({self.instance}) .'
