from lcall.DLClass import DLClass
from lcall.assertion import Assertion
from lcall.owlRdyInstance import OwlRdyInstance


class ClassAssertion(Assertion):
    """
    An object representing a class assertion in description logics
    """

    def __init__(self, concept: DLClass):
        """
        Initialization

        :param concept: the concept of the assertion
        """
        self.concept = concept
        # WARNING, this creates an instance
        self.instance = OwlRdyInstance(concept())

    def get_concept(self):
        return self.concept
    
    def get_instance(self):
        return self.instance

    def __repr__(self):
        return f'{self.concept}({self.instance})'
